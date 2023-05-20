# SUAP Scraper

Biblioteca python que raspa informações do aluno no [SUAP IFPB](https://suap.ifpb.edu.br).

## Propósito

Facilitar a produção de automações integradas ao SUAP(não encontrei um endpoint na API que retornasse os dados que eu quero, como notas do boletim, informações do aluno...).

## Instalação
```console
$ pip install suap-scraper
```
A biblioteca foi desenvolvida com python 3.9.5, mas já foi testada com python 3.7, então para python >=3.7 deve funcionar normalmente.

## Modo de Uso
Por enquanto a biblioteca só obtem informções do boletim.
```python
from suap_scraper import SUAP
import asyncio

async def main():
  suap = SUAP()
  try:
    suap.matricula = 'SUA_MATRICULA_AQUI' #opcional
    await suap.loginSessionId("SEU_SESSIONID_AQUI")
    boletim = await suap.getBoletim()
    print(boletim)
  finally:
    await suap.session.aclose()

if __name__ == '__main__':
  asyncio.run(main())

```
