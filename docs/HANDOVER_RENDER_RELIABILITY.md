# JARVIS 3.0 — Render Reliability Fix: Handover & Sign-off

| Field | Value |
|---|---|
| Project | JARVIS 3.0 Telegram bot |
| Change | Always-on hosting and bot hardening |
| Branch | `claude/cloud-work-no-laptop-1xmf3a` |
| Date | 2026-09-04 |
| Owner | Savio Paul |

## 1. Problem
Messages sent to JARVIS on Telegram received no reply. The message handler was verified working locally,
so updates were not reaching the process. Causes: Render free tier spins down after 15 minutes idle,
webhook registration only happened in `python bot.py`, handler crashes were swallowed silently, and the
update pool had only 2 threads.

## 2. What changed
| File | Change |
|---|---|
| `render.yaml` | Plan `free` → `starter` (no spin-down). Added `healthCheckPath: /health`. New env vars `BOT_WORKER_THREADS=8`, `KEEP_ALIVE_SECONDS=600`. |
| `Dockerfile` | Runs `gunicorn bot:app` (1 worker, 8 threads, 120 s timeout) instead of the Flask dev server. |
| `requirements.txt` | Added `gunicorn==22.0.0`. |
| `bot.py` | Webhook registered on every process start (works under gunicorn), `https://` added if Render gives a bare host, exception handler logs crashes, keep-alive self-ping, new `GET /status` diagnostics. Message handling logic untouched. |

## 3. Cost impact
Render Starter web service: about USD 7 per month. Redis stays on the free plan.

## 4. Deployment steps
1. Merge the PR to `main`. Render auto-deploys from the repo.
2. Render will prompt to confirm the plan change to Starter on the next blueprint sync. Approve it.
3. Watch the deploy log for `Webhook set to https://…` or `Webhook already registered`.

## 5. Test checklist
| # | Test | Expected | Pass |
|---|---|---|---|
| 1 | Open `https://<service>.onrender.com/health` | `Jarvis 3.0 is alive!` within 2 s | ☐ |
| 2 | Open `https://<service>.onrender.com/status` | `webhook_registered: true`, `last_error: null` | ☐ |
| 3 | Send `/start` on Telegram | Welcome message within 5 s | ☐ |
| 4 | Send `hello` | "JARVIS thinking…" then a reply | ☐ |
| 5 | Send a photo | "inspecting image…" then a description | ☐ |
| 6 | Send `/research test topic` and immediately `hello` in parallel | Second message still answered while research runs | ☐ |
| 7 | Wait 30 minutes idle, then send `hello` | Reply within 5 s (no cold start) | ☐ |
| 8 | Render → Logs after a deliberate bad command | Line starting `Unhandled error in message handler` | ☐ |
| 9 | Render → Manual Deploy → Restart | Log shows webhook registered again; bot replies | ☐ |

## 6. Rollback
Revert the PR. Render redeploys the previous image. Set plan back to `free` in the dashboard if needed.

## 7. Sign-off
| Role | Name | Date | Signature |
|---|---|---|---|
| Developer | | | |
| Stakeholder / Product owner | Savio Paul | | |
| Tester | | | |

Accepted: ☐ Yes  ☐ No (comments below)

Comments:
