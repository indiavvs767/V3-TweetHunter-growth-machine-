import os
import json
import time
import logging
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
from utils import load_json, save_state, now_ts

load_dotenv()
logger = logging.getLogger(__name__)

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# DM endpoint (v1.1)
AUTO_DM_URL = "https://api.twitter.com/1.1/direct_messages/events/new.json"
FOLLOWERS_URL = "https://api.twitter.com/1.1/followers/ids.json?stringify_ids=true&count=5000"
STATE_FILE = "store/state.json"
DM_TEMPLATES = load_json(os.getenv("DM_TEMPLATES_FILE", "templates/dm_sequence.json"))

oauth = OAuth1Session(API_KEY, client_secret=API_SECRET, resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_SECRET)

def get_followers_ids():
    resp = oauth.get(FOLLOWERS_URL)
    if resp.status_code != 200:
        logger.error("Followers fetch failed: %s %s", resp.status_code, resp.text)
        return []
    data = resp.json()
    return [str(x) for x in data.get("ids", [])]

def send_dm(user_id, text):
    payload = {
        "event": {
            "type": "message_create",
            "message_create": {
                "target": {"recipient_id": user_id},
                "message_data": {"text": text}
            }
        }
    }
    resp = oauth.post(AUTO_DM_URL, json=payload)
    if resp.status_code in (200,201):
        logger.info("Sent DM to %s", user_id)
        return True
    else:
        logger.error("DM failed %s: %s", resp.status_code, resp.text)
        return False

def run_autodm_cycle():
    state = load_json(STATE_FILE)
    seen = set(state.get("seen_followers", []))
    followers = get_followers_ids()
    new_followers = [f for f in followers if f not in seen]
    logger.info("Found %s new followers.", len(new_followers))
    for user_id in new_followers:
        # send first DM instantly
        first = DM_TEMPLATES[0]["text"]
        send_dm(user_id, first)
        # record
        seen.add(user_id)
        state["seen_followers"] = list(seen)
        save_state(STATE_FILE, state)
        # schedule followup DMs by storing next send times
        # we append to state a mapping for scheduled DMs
        state.setdefault("scheduled_dms", []).append({
            "user_id": user_id,
            "template_index": 1,
            "next_send_ts": now_ts() + int(DM_TEMPLATES[1]["delay_hours"]*3600)
        })
        save_state(STATE_FILE, state)
    # process scheduled
    scheduled = state.get("scheduled_dms", [])
    remaining = []
    for job in scheduled:
        if now_ts() >= job["next_send_ts"]:
            idx = job["template_index"]
            if idx < len(DM_TEMPLATES):
                text = DM_TEMPLATES[idx]["text"]
                ok = send_dm(job["user_id"], text)
                if ok:
                    # schedule next
                    job["template_index"] = idx + 1
                    if job["template_index"] < len(DM_TEMPLATES):
                        job["next_send_ts"] = now_ts() + int(DM_TEMPLATES[job["template_index"]]["delay_hours"]*3600)
                        remaining.append(job)
                else:
                    # keep job for retry later
                    job["next_send_ts"] = now_ts() + 3600
                    remaining.append(job)
        else:
            remaining.append(job)
    state["scheduled_dms"] = remaining
    save_state(STATE_FILE, state)
