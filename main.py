import requests
import sys
from bs4 import BeautifulSoup
from limpar_dados import sanitizar_saida
import json
import time
import os
from dotenv import load_dotenv

class SUAP:
  ua_padrao = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36.'}

  def __init__(self, matricula, senha, user_agent=ua_padrao):
    self.matricula = matricula
    self.senha = senha
    self.user_agent = user_agent
    self.session = requests.Session()
    self.session.headers.update(user_agent)

  def getInitialPage(self):
    res = self.session.get('https://suap.ifpb.edu.br')
    return res

  def getCookiesInitialPage(self, initial_page):

    soup = BeautifulSoup(initial_page.text, 'html.parser')
    middleware_csrf = soup.find(
      'input',
      attrs = {'name': 'csrfmiddlewaretoken'}
      )['value']

    csrf = initial_page.cookies['csrftoken']
    session_id = initial_page.cookies['sessionid']

    return [ middleware_csrf, csrf, session_id ]


  def loginSUAP(self, session_id, csrf, middleware_csrf):


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
        "referer": "https://suap.ifpb.edu.br/accounts/login/?next=/",
        "upgrade-insecure-requests": "1"
      }

    body = "csrfmiddlewaretoken="+ csrf +"&username="+str(self.matricula)+"&password="+self.senha+"&this_is_the_login_form=1&next=%2F&g-recaptcha-response="

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
    res = self.session.send(req)

    return res

  def getBoletimPage(self, session_id, csrf):

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
      "referrer": "https://suap.ifpb.edu.br/edu/aluno/"+str(self.matricula)+"/?tab=boletim",
      "referrerPolicy": "same-origin",
      "method": "GET",
      "mode": "cors",
      "credentials": "include",
      "mode": "cors"
      }

    req = requests.Request("GET", "https://suap.ifpb.edu.br/edu/aluno/"+str(self.matricula)+"/?tab=boletim", cookies={'sessionid': session_id, 'csrftoken': csrf}, headers=headers, json=req_json)

    req = req.prepare()
    res = self.session.send(req)
    html_content = res.text

    return html_content

  def createJSON(self, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    with open('boletim_html.txt', 'w') as html_arq:
      html_arq.write(str(soup.tbody))

    dic_materias = sanitizar_saida("boletim_html.txt", self.session)
    boletim_json = json.dumps(
      dic_materias, sort_keys=True, indent=2, ensure_ascii=False
    )

    with open('boletim.json', 'w') as json_arq:
      json_arq.write(boletim_json)

    return boletim_json

def main():
  load_dotenv()
  matricula = os.getenv("SUAP_MATRICULA")
  senha = os.getenv("SUAP_SENHA")
  suap = SUAP(matricula, senha)

  initial_page = suap.getInitialPage()
  middleware_csrf, csrf, session_id = suap.getCookiesInitialPage(initial_page)
  res = suap.loginSUAP(session_id, csrf, middleware_csrf)

  try:
    session_id = res.cookies['sessionid']
  except Exception as e:
    print(e)
    sys.exit(1)
  try:
    csrf = res.cookies['csrftoken']
  except:
    pass

  html_content = suap.getBoletimPage(session_id, csrf)
  boletim_json = suap.createJSON(html_content)

  suap.session.close()

  return boletim_json


if __name__== "__main__":
  print(main())
