def somaMedias(boletim):
  notas = {}
  items = boletim.items()
  for mat, bims in items:
    notas[mat] = 0
    for nome, bim in bims.items():
      if bim == '-':
        continue
      a1, a2, re = [int(i) if i != '-' else 0 for i in [bim['A1'], bim['A2'], bim['RE']]]
      media = (a1 + a2) // 2
      nota = media if (media > re) else re
      notas[mat] += nota
  return notas

def quantoFaltaMedia(notas):
    passou = 0
    quant_falta = {}
    for mat, nota in notas.items():
      mat = mat[mat.find('-') + 2::]
      falta = 280 - nota
      quant_falta[mat] = falta
    return quant_falta

def mensagemQuantoFalta(quanto_falta):
  msg = ''
  passou = 0
  for mat, falta in quanto_falta.items():
    msg += mat + ':\n'
    if falta < 0:
      msg += 'jah passou\n\n'
      passou += 1
      continue
    msg += f'faltam {falta} pontos nah media pro c passar\n\n'
  if passou:
    msg += f'Você já passou em {passou}/{len(quanto_falta)} materias(genio, apenas.)\n'
  return msg

if __name__ == '__main__':
  import json

  boletim = {}
  with open('boletim.json') as f:
    boletim = json.loads(f.read())

  soma_medias = somaMedias(boletim)
  quanto_falta = quantoFaltaMedia(soma_medias)
  msg = mensagemQuantoFalta(quanto_falta)

  with open('falta.txt', 'w') as f:
    f.write(msg)
  print(msg)
