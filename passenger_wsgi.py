import sys, os
INTERP = os.path.expanduser("~/domains/nlpers.ru/.venv/python311/bin/python3.11")

if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

from NLPers.wsgi import application