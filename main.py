import requests
import sys
from os import environ
from bs4 import BeautifulSoup
from limpar_dados import sanitizar_saida
import json
import time

session = requests.Session()
res = session.get('https://suap.ifpb.edu.br')

matricula = environ['SUAP_MATRICULA']
senha = environ['SUAP_SENHA']

#primeira req ^^

soup = BeautifulSoup(res.text, 'html.parser')
middleware_csrf = soup.find(
  'input',
  attrs = {'name': 'csrfmiddlewaretoken'}
  )['value']

csrf = res.cookies['csrftoken']
session_id = res.cookies['sessionid']

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1"
  }

body = "csrfmiddlewaretoken="+ middleware_csrf +"&username="+matricula+"&password="+senha+"&this_is_the_login_form=1&next=%2F"

req_json = {
  "referrer": "https://suap.ifpb.edu.br",
  "referrerPolicy": "same-origin",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
}

req = requests.Request("POST", "https://suap.ifpb.edu.br/accounts/login/?next=/", headers=headers, data=body, json=req_json, cookies={
  'csrftoken': csrf, 'sessionid': session_id
  })



req = req.prepare()
res = session.send(req)

time.sleep(2)
#segunda req ^^

try:
  session_id = res.cookies['sessionid']
except Exception as e:
  print(res.text)
  session.close()
  print('Falha autenticação:', e)
  sys.exit(1)
try:
  csrf = res.cookies['csrftoken']
except:
  pass

headers = {
    "accept": "*/*",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "x-requested-with": "XMLHttpRequest"
  }
req_json = {
  "referrer": "https://suap.ifpb.edu.br/edu/aluno/"+matricula+"/?tab=boletim",
  "referrerPolicy": "same-origin",
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
  }

req = requests.Request("GET", "https://suap.ifpb.edu.br/edu/aluno/"+matricula+"/?tab=boletim", cookies={'sessionid': session_id, 'csrftoken': csrf}, headers=headers, json=req_json)
req = req.prepare()
res = session.send(req)

#terceira req ^^
#tratar dados

html_content = res.text
session.close()
soup = BeautifulSoup(html_content, 'html.parser')


with open('boletim_html.txt', 'w') as arq:
  arq.write(str(soup.tbody))

dic_materias = sanitizar_saida("boletim_html.txt")
with open('boletim.json', 'w') as arq:
  arq.write(
    json.dumps(dic_materias, sort_keys=True, indent=2, ensure_ascii=False)
  )

