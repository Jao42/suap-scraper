from pandas import read_html

def pegarDetalhar(link):

  det = read_html(link)[0]
  notas = dict(zip(det['Sigla'], det['Nota Obtida']))
  return notas
