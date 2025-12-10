import os
import time
import random
import logging
from dotenv import load_dotenv
import tweepy
from utils import load_json, save_state, save_state as _save_state_fn

load_dotenv()
logger = logging.getLogger(__name__)

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

REPLY_BANK_PATH = os.getenv("REPLY_BANK_FILE", "templates/replies.json")
REPLY_BANK = load_json(REPLY_BANK_PATH)
STATE_FILE = "store/state.json"

MAX_REPLIES_PER_HOUR = int(os.getenv("MAX_REPLIES_PER_HOUR", "6"))
MIN_DELAY = int(os.getenv("MIN_REPLY_DELAY_SECONDS", "4"))
MAX_DELAY = int(os.getenv("MAX_REPLY_DELAY_SECONDS", "12"))

def load_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def send_reply(tweet_id, text):
    try:
        resp = api.update_status(status=text, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
        logger.info("Replied to %s", tweet_id)
        return resp
    except Exception as e:
        logger.exception("Error replying: %s", e)
        return None

def process_queue(reply_queue):
    state = load_state()
    replies_sent_hour = 0
    for item in list(reply_queue):
        if replies_sent_hour >= MAX_REPLIES_PER_HOUR:
            logger.info("Reached hourly reply cap (%s). Stopping.", MAX_REPLIES_PER_HOUR)
            break
        tweet_id = item["tweet_id"]
        # avoid duplicate safety
        if tweet_id in state.get("replied_tweets", {}):
            reply_queue.remove(item)
            continue
        reply_text = random.choice(REPLY_BANK)
        # add subtle personalization
        reply_text = reply_text + " — The Future Playbook"
        delay = random.randint(MIN_DELAY, MAX_DELAY)
        logger.info("Sleeping %s seconds before replying to %s", delay, tweet_id)
        time.sleep(delay)
        r = send_reply(tweet_id, reply_text)
        if r:
            # record
            state.setdefault("replied_tweets", {})[tweet_id] = {
                "reply_text": reply_text,
                "ts": int(time.time())
            }
            _save_state_fn(STATE_FILE, state)
            replies_sent_hour += 1
            reply_queue.remove(item)
    return reply_queue
