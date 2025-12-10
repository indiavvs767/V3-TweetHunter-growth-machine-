import os
from dotenv import load_dotenv

load_dotenv()

def getenv_bool(key, default=False):
    v = os.getenv(key, str(default)).lower()
    return v in ["1", "true", "yes", "on"]

DRY_RUN = getenv_bool("DRY_RUN", False)
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
