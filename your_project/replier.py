import time
import random
from logger import logger
from config import DRY_RUN
from twitter_api import client  # your wrapper

MAX_RETRIES = 5

def exponential_backoff(retry):
    # jitter + backoff
    base = 2 ** retry
    sleep_time = base + random.uniform(0, 1)
    return min(sleep_time, 60)  # hard cap 60s


def send_reply(tweet_id, text):
    if DRY_RUN:
        logger.info(f"[DRY_RUN] Would reply to {tweet_id}: {text}")
        return {"status": "dry_run"}

    retry = 0

    while retry < MAX_RETRIES:
        try:
            logger.debug(f"Sending reply → {tweet_id}: {text}")

            resp = client.create_tweet(
                text=text,
                reply={"in_reply_to_tweet_id": tweet_id}
            )

            logger.info(f"[SENT] reply to {tweet_id}")
            return resp

        except Exception as e:
            logger.warn(f"[ERROR] Reply failed: {e}")

            retry += 1
            wait = exponential_backoff(retry)
            logger.warn(f"[BACKOFF] Retry {retry}/{MAX_RETRIES} in {wait:.2f}s")
            time.sleep(wait)

    logger.error("[FAILED] Max retries exceeded for reply")
    return None
