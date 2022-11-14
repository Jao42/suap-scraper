from dotenv import load_dotenv
import os
from SUAP import SUAP

load_dotenv()
matricula = os.getenv("SUAP_MATRICULA")
senha = os.getenv("SUAP_SENHA")

suap = SUAP(matricula, senha)
boletim = suap.getBoletim()
suap.session.close()
