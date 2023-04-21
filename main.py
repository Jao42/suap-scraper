from SUAP import SUAP
import os

session_id = os.getenv("SUAP_SESSION_ID")

suap = SUAP()
suap.loginSessionId(session_id)
boletim = suap.getBoletim()
print(boletim)
