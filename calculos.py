def somaMedias(boletim):
  notas = {}
  items = boletim.items()
  for mat, bims in items:
    notas[mat] = 0
    bimestres = [bims['E1'], bims['E2'], bims['E3'], bims['E4']]
    for bim_notas in bimestres:
      if bim_notas == None:
        continue
      a1, a2, re = [int(i) if i != None else 0 for i in [bim_notas['A1'], bim_notas['A2'], bim_notas['RE']]]
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

def pegarQuantoFalta(boletim):
  soma_medias = somaMedias(boletim)
  quanto_falta = quantoFaltaMedia(soma_medias)
  msg = mensagemQuantoFalta(quanto_falta)

  return msg

if __name__ == '__main__':
  import json

  boletim = {}
  with open('boletim.json') as f:
    boletim = json.loads(f.read())

  msg = pegarQuantoFalta(boletim)

  with open('falta.txt', 'w') as f:
    f.write(msg)
  print(msg)
