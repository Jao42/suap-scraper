import requests
import sys
from bs4 import BeautifulSoup
from limpar_dados import sanitizar_saida
import json
import time
import os
from config import *

class SUAP:

  def __init__(self, matricula, senha, user_agent=UA_PADRAO):
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

    body = "csrfmiddlewaretoken="+ middleware_csrf +"&username="+str(self.matricula)+"&password="+self.senha+"&this_is_the_login_form=1&next="

    if campo_captcha:
      body += "&g-recaptcha-response="


    req = requests.Request("POST", "https://suap.ifpb.edu.br/accounts/login/?next=/", headers=HEADER_LOGIN, data=body, json=REQ_JSON_LOGIN, cookies={
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


    req_json = REQ_JSON_BOLETIM
    req_json["referrer"] = "https://suap.ifpb.edu.br/edu/aluno/" + str(self.matricula) + "/?tab=boletim"

    req = requests.Request("GET", "https://suap.ifpb.edu.br/edu/aluno/"+str(self.matricula)+"/?tab=boletim", cookies={'sessionid': self.session_id, 'csrftoken': self.csrf}, headers=HEADER_BOLETIM, json=req_json)

    req = req.prepare()
    res = self.session.send(req)
    html_content = res.text

    return html_content

  def __createBoletimJSON(self, html_content):

    with open('./tmp/boletim.html', 'w') as html_arq:
      html_arq.write(html_content)

    dic_materias = sanitizar_saida("./tmp/boletim.html", self.session)
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
