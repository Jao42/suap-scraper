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
    self.session_id, self.csrf = self.__loginSUAP()

  def __getInitialPage(self):
    res = self.session.get('https://suap.ifpb.edu.br')
    return res

  def __getCookiesInitialPage(self, initial_page):

    soup = BeautifulSoup(initial_page.text, 'html.parser')
    middleware_csrf = soup.find(
      'input',
      attrs = {'name': 'csrfmiddlewaretoken'}
      )['value']

    csrf = initial_page.cookies['csrftoken']
    session_id = initial_page.cookies['sessionid']

    return [ middleware_csrf, csrf, session_id ]


  def __loginSUAP(self, campo_captcha=False):

    initial_page = self.__getInitialPage()
    middleware_csrf, csrf, session_id = self.__getCookiesInitialPage(initial_page)


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

    body = "csrfmiddlewaretoken="+ middleware_csrf +"&username="+str(self.matricula)+"&password="+self.senha+"&this_is_the_login_form=1&next="

    if campo_captcha:
      body += "&g-recaptcha-response="

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

    session_id = res.cookies['sessionid']
    try:
      csrf = res.cookies['csrftoken']
    except:
      pass


    return [ session_id, csrf ]

  def __getBoletimPage(self):

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

    req = requests.Request("GET", "https://suap.ifpb.edu.br/edu/aluno/"+str(self.matricula)+"/?tab=boletim", cookies={'sessionid': self.session_id, 'csrftoken': self.csrf}, headers=headers, json=req_json)

    req = req.prepare()
    res = self.session.send(req)
    html_content = res.text

    return html_content

  def __createBoletimJSON(self, html_content):

    with open('boletim.html', 'w') as html_arq:
      html_arq.write(html_content)

    dic_materias = sanitizar_saida("boletim.html", self.session)
    boletim_json = json.dumps(
      dic_materias, sort_keys=True, indent=2, ensure_ascii=False
    )

    with open('boletim.json', 'w') as json_arq:
      json_arq.write(boletim_json)

    return boletim_json

  def getBoletim(self):
    html_boletim = self.__getBoletimPage()
    boletim = self.__createBoletimJSON(html_boletim)
    return boletim





def main():
  load_dotenv()
  matricula = os.getenv("SUAP_MATRICULA")
  senha = os.getenv("SUAP_SENHA")

  suap = SUAP(matricula, senha)
  boletim = suap.getBoletim()
  suap.session.close()

  print(boletim)


if __name__== "__main__":
  main()
