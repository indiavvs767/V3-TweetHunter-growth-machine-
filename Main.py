import logging
import time
import threading
import os
from dotenv import load_dotenv
from poller import poll_recent_and_enqueue, load_state
from replier import process_queue
from autodm import run_autodm_cycle
from scheduler import start as start_scheduler

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"))
logger = logging.getLogger("future-playbook")

reply_queue = []

def poller_loop():
    while True:
        try:
            poll_recent_and_enqueue(reply_queue)
        except Exception as e:
            logger.exception("Poller error: %s", e)
        time.sleep(30)  # poll every 30s

def replier_loop():
    while True:
        try:
            if reply_queue:
                process_queue(reply_queue)
        except Exception as e:
            logger.exception("Replier error: %s", e)
        time.sleep(10)

def autodm_loop():
    while True:
        try:
            run_autodm_cycle()
        except Exception as e:
            logger.exception("AutoDM error: %s", e)
        time.sleep(300)  # every 5 minutes

if __name__ == "__main__":
    # start scheduler in thread
    t_sched = threading.Thread(target=start_scheduler, daemon=True)
    t_sched.start()

    t1 = threading.Thread(target=poller_loop, daemon=True)
    t2 = threading.Thread(target=replier_loop, daemon=True)
    t3 = threading.Thread(target=autodm_loop, daemon=True)

    t1.start(); t2.start(); t3.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutting down.")
