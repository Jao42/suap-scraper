from suap_scraper import SUAP
import os
import sys
import json
from jsondiff import diff
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from dotenv import load_dotenv
from mensagem import mensagem_formatada
import time
import asyncio

load_dotenv()

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIRECTORY_PATH = os.path.dirname(SCRIPT_PATH)
BOLETIM_PATH = os.path.join(SCRIPT_DIRECTORY_PATH, "boletim.json")
boletim_salvo = ''
with open(BOLETIM_PATH, 'r') as f:
  boletim_salvo = f.read()
session_id = os.getenv("SUAP_SESSION_ID")

async def main():
  global boletim_salvo
  suap = SUAP()
  await suap.loginSessionId(session_id)
  novo_boletim = await suap.getBoletim()
  novas_notas = diff(boletim_salvo, novo_boletim, load=True, dump=False, marshal=True)
  if not novas_notas:
    print('Sem novas notas!')
    return

  dumped_json = json.dumps(
        novas_notas, sort_keys=True, indent=2, ensure_ascii=False
        )
  try:
    msg_email = mensagem_formatada(novas_notas)
  except Exception as e:
    msg_email = dumped_json
    print(e)

  message = Mail(
      to_emails='cavalcante.joao@protonmail.ch',
      subject='Novas notas no SUAP',
      plain_text_content=msg_email
    )

  message.from_email = From(
      email="suap_notificacoes@jao42.dev.br",
      name="SUAP Notificações",
      p=1
  )
  try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    with open(BOLETIM_PATH, 'w') as f:
      boletim_salvo = f.write(novo_boletim)

  except Exception as e:
    print(e.message)

asyncio.run(main())
