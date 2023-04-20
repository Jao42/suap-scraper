from bs4 import BeautifulSoup
import sys
import json
from pandas import read_html


INDICES_NOTAS_PADRAO = [7, 9, 11, 13, 15, 18]
LABELS_NOTAS_TABLE = ['E1', 'E2', 'E3', 'E4', 'MD', 'CONCEITO']


def pegar_detalhar(link):

  det = read_html(link)[0]
  for i in range(len(det['Nota Obtida'])):
    if det['Nota Obtida'][i] == '-':
      det['Nota Obtida'][i] = None
  notas = dict(zip(det['Sigla'], det['Nota Obtida']))
  return notas

def tratar_notas_etapas(materia_notas_tds, session):
  etapas = {}
  for i in range(len(INDICES_NOTAS_PADRAO)):
    label = LABELS_NOTAS_TABLE[i]
    notas_materia = materia_notas_tds[i]
    valor = ''

    soup = BeautifulSoup(str(notas_materia), 'html.parser')
    if (soup.a is not None):
      link = 'https://suap.ifpb.edu.br' + soup.a['href']
      res = session.get(link)
      valor = pegar_detalhar(res.text)

    else:
      valor = soup.get_text().replace(' ', '').replace('\n', '').replace('\\n', '')
      valor = valor if valor != '-' else None
    etapas[label] = valor
  return etapas


def tem_colspan(tag):
  return tag.has_attr('colspan')


def criar_indices_colspan(indices_notas, indices_colspans):
  indices_notas_materia = indices_notas[::]
  for i in indices_colspans:
    for j in range(len(indices_notas)):
      if indices_notas_materia[j] > i:
        indices_notas_materia[j] -= 1
  return indices_notas_materia


def sanitizar_saida(arq, session):


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

    indices_colspan = [i for i in range(len(materia_tds)) if tem_colspan(materia_tds[i])]
    indices_notas_materia = criar_indices_colspan(INDICES_NOTAS_PADRAO, indices_colspan)
    materia_notas_tds = [materia_tds[i] for i in indices_notas_materia]

    materias[disciplina] = tratar_notas_etapas(materia_notas_tds, session)
  return materias

