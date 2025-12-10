# TweetHunter V3 — Growth Machine (Auto-Reply + Auto-DM)

Automates:
- Monitor keywords & tracked accounts
- Auto-reply with a reply bank (configurable)
- Auto-DM new followers with a multi-step funnel
- Scheduler for posting content
- Basic analytics/logging and rate limit handling

⚠️ Requirements: X (Twitter) developer keys with read/write and DM permissions.

## Quick start

1. Clone repo
2. Create `.env` (see `.env.example`)
3. `pip install -r requirements.txt`
4. Run
   - `python main.py` (runs poller + scheduler)
   - Or deploy with Docker / systemd on a server

## Features
- Keyword + account monitoring (poll `recent` endpoint)
- Reply queue with random delays and hourly caps
- Auto-DM funnel for new followers
- Simple scheduler for tweets/threads
- Safe guards (rate-limit aware, cooldowns, persistent state)

## Files
- `main.py` — entrypoint
- `poller.py` — polls recent tweets based on keywords/accounts and queues them
- `replier.py` — sends replies from reply bank with throttling
- `autodm.py` — handles auto-DM welcome + sequence for followers
- `scheduler.py` — schedules posts
- `store/` — local JSON state (followers seen, replies sent)
- `templates/` — reply & DM templates
- `Dockerfile`, `docker-compose.yml` — optional deployment

## Notes
- Configure sensible caps in `.env` (e.g., MAX_REPLIES_PER_HR).
- Respect X/Twitter TOS. Avoid spamming.

