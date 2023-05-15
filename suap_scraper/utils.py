from selectolax.parser import HTMLParser
import sys
import json
import asyncio
from suap_scraper.config import *

def tratar_notas_detalhar(html_detalhar):
  notas = {}
  tree = HTMLParser(html_detalhar)
  trs_nodes = tree.css('tbody > tr')
  for tr_node in trs_nodes:
    tr_tds = tr_node.css('td')
    nota = tr_tds[4].text()
    sigla_av = tr_tds[0].text()
    notas[sigla_av] = None if nota == '-' else int(nota)

  return notas

async def tratar_etapas_tds(materia_etapas_tds, session):
  etapas = {}
  tasks = []
  etapas_com_link = []
  etapas_td = zip(LABELS_NOTAS_TABLE, materia_etapas_tds)
  for etapa, td in etapas_td:
    link = td.css_first('a')
    texto_td = td.text().strip()
    notas = texto_td
    if link is not None:
      etapas_com_link.append(etapa)
      tasks.append(asyncio.create_task(session.get(LINK_SUAP + link.attributes['href'])))
    etapas[etapa] = notas if notas != '-' else None

  responses = await asyncio.gather(*tasks)
  for i in range(len(etapas_com_link)):
    html_detalhar = responses[i].text
    notas = tratar_notas_detalhar(html_detalhar)
    etapas[etapas_com_link[i]] = notas
  return etapas


def tem_colspan(tag):
  return ('colspan' in list(tag.attributes.keys()))

def criar_indices_colspan(indices_notas, indices_colspans):
  indices_notas_materia = indices_notas[::]
  for i in indices_colspans:
    for j in range(len(indices_notas)):
      if indices_notas_materia[j] > i:
        indices_notas_materia[j] -= 1
  return indices_notas_materia


def materias_etapas_tds(boletim_html):

  tree = HTMLParser(boletim_html)
  materias_tr = tree.css('.borda > tbody > tr')
  materias = {}

  for i in range(len(materias_tr)):

    materia_tr = materias_tr[i]
    materia_tds = materia_tr.css('td')

    disciplina_node = materia_tds[1]
    disciplina = (disciplina_node
    .text()
    .replace('\n', '')
    .strip()
    .replace('  ', ''))

    indices_colspan = [
      i for i in range(len(materia_tds)) if tem_colspan(materia_tds[i])
    ]
    indices_notas_materia = criar_indices_colspan(
      INDICES_NOTAS_PADRAO,
      indices_colspan
    )
    materia_etapas_tds = [materia_tds[i] for i in indices_notas_materia]

    materias[disciplina] = materia_etapas_tds
  return materias

async def parsear_boletim(boletim_html, session):
  materias = materias_etapas_tds(boletim_html)
  tasks = []
  boletim = {}
  disciplinas = materias.keys()

  for disciplina, materia_etapas_tds in materias.items():
    tasks.append(
      asyncio.create_task(
        tratar_etapas_tds(
      materia_etapas_tds,
      session
      )
    ))
  responses = await asyncio.gather(*tasks)
  for i in range(len(disciplinas)):
    boletim[list(disciplinas)[i]] = responses[i]
  return boletim
