import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
import tweepy
import random
from utils import load_json

load_dotenv()
logger = logging.getLogger(__name__)

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

SCHEDULE_FILE = "templates/scheduled_posts.json"

def post_text(text):
    try:
        api.update_status(status=text)
        logger.info("Posted scheduled tweet.")
    except Exception as e:
        logger.exception("Posting failed: %s", e)

def job_post_random():
    posts = load_json(SCHEDULE_FILE)
    text = random.choice(posts)
    post_text(text)

def start():
    scheduler = BackgroundScheduler()
    # sample schedule times; you can configure more granular times in env
    scheduler.add_job(job_post_random, 'cron', hour='8', minute='15')   # 8:15AM
    scheduler.add_job(job_post_random, 'cron', hour='13', minute='0')   # 1:00PM
    scheduler.add_job(job_post_random, 'cron', hour='19', minute='0')   # 7:00PM
    scheduler.start()
    logger.info("Scheduler started.")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
