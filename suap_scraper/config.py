UA_PADRAO = {'User-Agent': 'Oi, eu sou um bot que raspa o SUAP do IFPB. Disponivel em: https://github.com/Jao42/suap-scraper'}

HEADER_LOGIN = {
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


REQ_JSON_LOGIN = {
  "referrer": "https://suap.ifpb.edu.br",
  "referrerPolicy": "same-origin",
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
  }


HEADER_BOLETIM = {
  "accept": "*/*",
  "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "same-origin",
  "sec-gpc": "1",
  "x-requested-with": "XMLHttpRequest"
}

REQ_JSON_BOLETIM = {
  "referrerPolicy": "same-origin",
  "method": "GET",
  "mode": "cors",
  "credentials": "include",
  "mode": "cors"
  }

MSGS_ERRO = {"or favor, entre com um usuário  e senha corretos. Note que ambos os campos diferenciam maiúsculas e minúsculas.": "Matricula ou senha estao incorretos",
             "Por favor, corrija o erro abaixo.":"Captcha impediu o login(credenciais validas)"
             }

INDICES_NOTAS_PADRAO = [7, 9, 11, 13, 15, 16, 18]
LABELS_NOTAS_TABLE = ['E1', 'E2', 'E3', 'E4', 'MD', 'NAF', 'CONCEITO']
LINK_SUAP = 'https://suap.ifpb.edu.br'
