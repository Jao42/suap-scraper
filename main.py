import requests
import sys
from os import environ
from bs4 import BeautifulSoup
from limpar_dados import sanitizar_saida
import json
import time

matricula = environ['SUAP_MATRICULA']
senha = environ['SUAP_SENHA']
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36.'})

def initialPageRequest():
  res = session.get('https://suap.ifpb.edu.br')
  return res


def getCookiesInitialPage(initial_page):

  soup = BeautifulSoup(initial_page.text, 'html.parser')
  middleware_csrf = soup.find(
    'input',
    attrs = {'name': 'csrfmiddlewaretoken'}
    )['value']

  csrf = initial_page.cookies['csrftoken']
  session_id = initial_page.cookies['sessionid']

  return [ middleware_csrf, csrf, session_id ]



def loginReq(session_id, csrf, middleware_csrf):
  matricula = environ['SUAP_MATRICULA']
  senha = environ['SUAP_SENHA']


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

  body = "csrfmiddlewaretoken="+ csrf +"&username="+matricula+"&password="+senha+"&this_is_the_login_form=1&next=%2F"

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

  return res

def boletimPageRequest(session_id, csrf):
  req_json = {
    "mode": "cors"
    }


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
    "credentials": "include",
    "mode": "cors"
    }

  req = requests.Request("GET", "https://suap.ifpb.edu.br/edu/aluno/"+matricula+"/?tab=boletim", cookies={'sessionid': session_id, 'csrftoken': csrf}, headers=headers, json=req_json)

  req = req.prepare()
  res = session.send(req)
  html_content = res.text

  return html_content

def createJSON(html_content):
  soup = BeautifulSoup(html_content, 'html.parser')

  with open('boletim_html.txt', 'w') as html_arq:
    html_arq.write(str(soup.tbody))

  dic_materias = sanitizar_saida("boletim_html.txt")
  boletim_json = json.dumps(
    dic_materias, sort_keys=True, indent=2, ensure_ascii=False
  )

  with open('boletim.json', 'w') as json_arq:
    json_arq.write(boletim_json)

  return boletim_json

def main():

  initial_page = initialPageRequest()
  middleware_csrf, csrf, session_id = getCookiesInitialPage(initial_page)
  res = loginReq(session_id, csrf, middleware_csrf)

  try:
    session_id = res.cookies['sessionid']
  except Exception as e:
    print(e)
    sys.exit(1)
  try:
    csrf = res.cookies['csrftoken']
  except:
    pass

  html_content = boletimPageRequest(session_id, csrf)
  boletim_json = createJSON(html_content)


  return boletim_json


session.close()

if __name__== "__main__":
  boletim_json = main()
  print(boletim_json)

