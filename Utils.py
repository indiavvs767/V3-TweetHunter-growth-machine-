import os
import json
import time
from dotenv import load_dotenv
load_dotenv()

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def now_ts():
    return int(time.time())
