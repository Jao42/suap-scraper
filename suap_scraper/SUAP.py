import httpx
import asyncio
import sys
from bs4 import BeautifulSoup
from suap_scraper.utils import parsear_boletim
import json
import time
import os
from suap_scraper.config import *


class LoginError(Exception):
  """
  Gerar mensagens de erro ao n conseguir logar
  """


class SUAP:
  def __init__(self, user_agent=UA_PADRAO):
    self.user_agent = user_agent
    self.session = httpx.AsyncClient()
    self.session.headers.update(user_agent)

  async def loginCredenciais(self, matricula, senha, user_agent=UA_PADRAO):
    self.matricula = matricula
    self.senha = senha
    self.session_id, self.csrf = await self.__loginSUAP()

  async def loginSessionId(self, session_id, user_agent=UA_PADRAO):
    self.session_id = session_id
    self.session.cookies['sessionid'] = self.session_id
    logged = await self.__getInitialPage()
    self.matricula = logged.headers.get('user')
    self.csrf = ''
    self.senha = ''

  async def __getInitialPage(self):
    res = await self.session.get(LINK_SUAP)
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


  async def __loginSUAP(self, campo_captcha=False):
    initial_page = await self.__getInitialPage()
    middleware_csrf, csrf, session_id = self.__getCookiesInitialPage(
      initial_page
    )

    body = ("csrfmiddlewaretoken=" + middleware_csrf +
    "&username=" + str(self.matricula) +
    "&password=" + self.senha +
    "&this_is_the_login_form=1&next="
    )

    if campo_captcha:
      body += "&g-recaptcha-response="

    req = session.build_request("POST",
                           LINK_SUAP + "/accounts/login/?next=/",
                           headers=HEADER_LOGIN,
                           data=body,
                           json=REQ_JSON_LOGIN,
                           cookies={
                            'csrftoken': csrf,
                            'sessionid': session_id
                          }
                        )

    res = await self.session.send(req)

    try:
      session_id = res.cookies['sessionid']
    except KeyError:
      soup = BeautifulSoup(res.text, 'html.parser')
      erro = soup.find(class_="errornote")
      if erro == None:
        raise LoginError("Não foi possivel logar no SUAP")
      msg_erro = erro.get_text().strip()
      try:
        raise LoginError(MSGS_ERRO[msg_erro])
      except KeyError:
        raise LoginError(msg_erro)
    try:
      csrf = res.cookies['csrftoken']
    except:
      pass

    return [ session_id, csrf ]

  async def __getBoletimPage(self):
    req_json = REQ_JSON_BOLETIM
    req_json["referrer"] = (LINK_SUAP + "/edu/aluno/"
    + str(self.matricula)
    + "/?tab=boletim"
    )

    req = self.session.build_request("GET",
                           LINK_SUAP + "/edu/aluno/"
                           +str(self.matricula)
                           +"/?tab=boletim",
                           cookies={
                             'sessionid': self.session_id,
                             'csrftoken': self.csrf
                           },
                           headers=HEADER_BOLETIM,
                           json=req_json
                           )
    res = ''
    html_content = ''
    while req is not None:
      res = await self.session.send(req)
      req = res.next_request
    html_content = res.text

    return html_content

  async def __createBoletimJSON(self, html_content):
    dic_materias = await parsear_boletim(html_content, self.session)
    boletim_json = json.dumps(
      dic_materias, sort_keys=True, indent=2, ensure_ascii=False
    )

    return boletim_json

  async def getBoletim(self):
    html_boletim = await self.__getBoletimPage()
    boletim = await self.__createBoletimJSON(html_boletim)
    return boletim
