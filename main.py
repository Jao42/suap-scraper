import requests
import sys
from os import environ
from bs4 import BeautifulSoup

session = requests.Session()
req = requests.Request('GET', 'https://suap.ifpb.edu.br')
req = req.prepare()
res = session.send(req)
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

json = {
  "referrer": "https://suap.ifpb.edu.br",
  "referrerPolicy": "same-origin",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
}

req = requests.Request("POST", "https://suap.ifpb.edu.br/accounts/login/?next=/", headers=headers, data=body, json=json, cookies={
  'csrftoken': csrf, 'sessionid': session_id
  })



req = req.prepare()
res = session.send(req)

#segunda req ^^

try:
  session_id = res.cookies['sessionid']
except:
  pass
  print('Falha autenticação')
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
json = {
  "referrer": "https://suap.ifpb.edu.br/edu/aluno/"+matricula+"/?tab=boletim&&ano_periodo=2020_1",
  "referrerPolicy": "same-origin",
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
  }

req = requests.Request("GET", "https://suap.ifpb.edu.br/edu/aluno/"+matricula+"/?tab=boletim&ano_periodo=2020_1", cookies={'sessionid': session_id, 'csrftoken': csrf}, headers=headers, json=json)
req = req.prepare()
res = session.send(req)

#terceira req ^^

#tratar dados
html_content = res.text
soup = BeautifulSoup(html_content, 'html.parser')


with open('boletim_html.txt', 'w') as arq:
  arq.write(str(soup.tbody))

