from dotenv import load_dotenv
import os
from SUAP import SUAP

session_id = os.getenv("SUAP_SESSION_ID")

suap = SUAP()
suap.loginSessionId(session_id)
boletim = suap.getBoletim()
print(boletim)
