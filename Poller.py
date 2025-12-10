import os
import time
import logging
from utils import load_json, save_state, now_ts
from dotenv import load_dotenv
import tweepy
import json

load_dotenv()
logger = logging.getLogger(__name__)

BEARER = os.getenv("TWITTER_BEARER_TOKEN")
KEYWORDS = os.getenv("MONITOR_KEYWORDS", "").split(",")
ACCOUNTS = [a.strip() for a in os.getenv("MONITOR_ACCOUNTS", "").split(",") if a.strip()]
STATE_FILE = "store/state.json"

client = tweepy.Client(bearer_token=BEARER, wait_on_rate_limit=True)

def build_query():
    kw_q = " OR ".join([f'"{k.strip()}"' for k in KEYWORDS if k.strip()])
    acc_q = " OR ".join([f"from:{a}" for a in ACCOUNTS if a])
    parts = []
    if kw_q:
        parts.append(f"({kw_q})")
    if acc_q:
        parts.append(f"({acc_q})")
    # filter out retweets and replies for cleaner opportunities
    query = " ".join(parts) + " -is:retweet -is:reply lang:en"
    return query

def load_state():
    return load_json(STATE_FILE)

def save_state_local(state):
    save_state(STATE_FILE, state)

def poll_recent_and_enqueue(reply_queue, last_polled=None, max_results=25):
    query = build_query()
    logger.info("Searching tweets with query: %s", query)
    # Use start_time param to get tweets after last_polled
    tweets = client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=["author_id","created_at","public_metrics","text"])
    new_since = last_polled or now_ts()
    state = load_state()
    for t in tweets.data if tweets.data else []:
        tid = str(t.id)
        if tid in state.get("replied_tweets", {}):
            continue
        # eligibility: likes or retweets threshold
        metrics = t.public_metrics or {}
        popularity = metrics.get("retweet_count",0) + metrics.get("reply_count",0) + metrics.get("like_count",0)
        # simple threshold to target slightly-viral tweets
        if popularity >= 10:
            reply_queue.append({
                "tweet_id": tid,
                "author_id": t.author_id,
                "text": t.text,
                "popularity": popularity
            })
            logger.info("Enqueued tweet %s (pop=%s)", tid, popularity)
    state["last_polled"] = now_ts()
    save_state_local(state)
    return reply_queue
