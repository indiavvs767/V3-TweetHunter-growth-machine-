import time
import random
from logger import logger
from config import DRY_RUN
from twitter_api import client

MAX_RETRIES = 5

def exponential_backoff(retry):
    base = 2 ** retry
    return min(base + random.uniform(0, 1), 60)


def send_dm(user_id, text):
    if DRY_RUN:
        logger.info(f"[DRY_RUN] Would DM {user_id}: {text}")
        return {"status": "dry_run"}

    retry = 0
    while retry < MAX_RETRIES:
        try:
            logger.debug(f"Sending DM → {user_id}: {text}")

            resp = client.send_dm(user_id, text)

            logger.info(f"[SENT DM] to {user_id}")
            return resp

        except Exception as e:
            logger.warn(f"[ERROR] DM failed: {e}")

            retry += 1
            wait = exponential_backoff(retry)
            logger.warn(f"[BACKOFF] Retry {retry}/{MAX_RETRIES} in {wait:.2f}s")
            time.sleep(wait)

    logger.error("[FAILED] Max retries exceeded for DM")
    return None
