# JARVIS 3.0 — Project Memory for Claude

## What this is
Telegram bot ("JARVIS") built on Flask + pyTelegramBotAPI, deployed on Render via Docker
(`render.yaml`, `Dockerfile`). LLM providers: Gemini (primary), Groq, Ollama — see `providers.py`.
Memory in Redis (`memory.py`). Extra engines: website builder, 2D cartoon/video (moviepy+ffmpeg),
deep research, self-upgrade agents.

## Runtime shape
- Entry: `bot.py` exposes Flask `app`. Telegram → webhook `POST /<TELEGRAM_TOKEN>` → `bot.process_new_updates`.
- Handlers run in the telebot worker pool (`BOT_WORKER_THREADS`, default 8).
- Startup (`on_startup`) registers the webhook and starts a keep-alive self-ping; runs on import so it
  works under gunicorn. Set `BOT_SKIP_STARTUP=1` to import without side effects (tests).
- Diagnostics: `GET /health` (liveness), `GET /status` (webhook registered, pending updates, last error).
- Production server: gunicorn, 1 worker, 8 threads (Dockerfile CMD).

## Local test recipe
```
python -m venv v && ./v/bin/pip install -r requirements.txt
TELEGRAM_TOKEN=123:dummy PORT=5055 ./v/bin/gunicorn bot:app --bind 0.0.0.0:5055 --workers 1 --threads 8
curl localhost:5055/health
curl -X POST localhost:5055/123:dummy -H 'Content-Type: application/json' \
  -d '{"update_id":1,"message":{"message_id":10,"date":1725000000,"chat":{"id":42,"type":"private"},"from":{"id":42,"is_bot":false,"first_name":"S"},"text":"hello"}}'
```
Expect the log line `Unhandled error ... api.telegram.org` when offline (handler reached Telegram).

## Session log
### 2026-09-04 — Render reliability fix (branch `claude/cloud-work-no-laptop-1xmf3a`)
- Symptom: bot silent on Telegram. Code verified locally (all modules import, handler replies).
  Root cause is deployment: Render free tier sleeps / webhook drops / OOM on video jobs / 2-thread pool.
- Changes: gunicorn, 8 worker threads, logged handler exceptions, webhook registration on every
  process start with https normalisation, keep-alive self-ping, `/status` endpoint,
  Render plan `free` → `starter`, `healthCheckPath: /health`.
- Not changed: any message-handling logic, providers, brain.
- Handover + test checklist: `docs/HANDOVER_RENDER_RELIABILITY.md`.

## Open items
- Add Claude (Anthropic API) as a provider in `providers.py` / `brain.py` (user to confirm).
- Render free Redis expires after 30 days; confirm `jarvis-memory` is still alive.
