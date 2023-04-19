from bs4 import BeautifulSoup
import sys
import json
from pandas import read_html


def pegar_detalhar(link):

  det = read_html(link)[0]
  for i in range(len(det['Nota Obtida'])):
    if det['Nota Obtida'][i] == '-':
      det['Nota Obtida'][i] = None
  notas = dict(zip(det['Sigla'], det['Nota Obtida']))
  return notas

def sanitizar_saida(arq, session):

  INDICES_NOTAS_PADRAO = [7, 9, 11, 13, 15, 18]
  LABELS_NOTAS_TABLE = ['E1', 'E2', 'E3', 'E4', 'MD', 'CONCEITO']

  file = open(arq, 'r')
  html_file = file.read()
  file.close()

  soup = BeautifulSoup(html_file, 'html.parser')
  corpo_tabela_soup = soup.tbody
  materias_html = corpo_tabela_soup.find_all('tr')

  materias = {}

  for i in range(len(materias_html)):

    soup = BeautifulSoup(str(materias_html[i]), 'html.parser')
    materia_tds = soup.find_all('td')

    disciplina_soup = materia_tds[1]
    disciplina = disciplina_soup.get_text().replace('\n', '').strip().replace('  ', '')
    materias[disciplina] = {}
    materia_medias_ref = [materias_html_td[7], materias_html_td[9], materias_html_td[11], materias_html_td[13], materias_html_td[15], materias_html_td[18]]

    for i in range(len(labels)):
      label = labels[i]
      notas_materia = materia_medias_ref[i]

      soup = BeautifulSoup(str(notas_materia), 'html.parser')
      if (soup.a is not None):
        link =  'https://suap.ifpb.edu.br' + soup.a['href']
        res = session.get(link)
        valor = pegar_detalhar(res.text)

      else:
        valor = soup.get_text().replace(' ', '').replace('\n', '').replace('\\n', '')
        valor = valor if valor != '-' else None


      materias[disciplina][label] = valor
  return materias

