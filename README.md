<div align="center">

<img src="docs/assets/brand/icon.svg" width="96" alt="ITSD Reminder icon: a white notification bell on a crimson rounded square">

# 🤖 ITSD Reminder Bot

**A Slack bot that reminds people to pick a category on their IT Service Desk ticket, once, in the ticket's thread**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-Web%20API-4A154B?logo=slack&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
[![CI](https://github.com/CaputoDavide93/ITSD-Reminder/actions/workflows/ci.yml/badge.svg)](https://github.com/CaputoDavide93/ITSD-Reminder/actions/workflows/ci.yml)

[Why](#-why-it-exists) • [Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#️-architecture) • [Configuration](#️-configuration) • [Docs](docs/README.md) • [Contributing](#-contributing)

</div>

---

## 💡 Why it exists

People open a ticket in the Service Desk channel and forget to choose a category. Nothing routes the ticket until someone notices, and the IT team ends up asking the same person the same question in a thread.

This bot asks for you. It watches one Slack channel. When a message is older than your threshold and the HelpDesk bot has not replied to it, the bot replies in that thread with a reminder, once per ticket.

| | ITSD Reminder | Chasing by hand | A fixed-time announcement in the channel |
|---|---|---|---|
| Knows which tickets are still waiting | Yes: no HelpDesk bot reply in the thread after the threshold | Someone has to look | No, it goes to everyone |
| Replies in the ticket's own thread | Yes, mentioning the author | Yes | No |
| Repeats itself on the same ticket | No: bot user ID check plus a JSON log of reminded threads | Easily | On every run |
| Needs something running | One small container | No | No |

The trade-off: you need a Slack app, a bot token and a container that stays up. The bot also treats a HelpDesk bot reply as proof a ticket was handled, so it only suits setups where that bot answers every processed ticket.

---

## 🚀 Quick Start

You need Docker with Compose, a Slack app with a bot token, the ID of the channel, and the ID of your HelpDesk bot. [docs/setup.md](docs/setup.md) walks through each of those.

1. **Clone and configure.**
   ```bash
   git clone https://github.com/CaputoDavide93/ITSD-Reminder.git
   cd ITSD-Reminder
   cp .env.example .env
   nano .env   # SLACK_BOT_TOKEN, CHANNEL_ID, HELPDESK_BOT_ID
   ```
2. **Start it.**
   ```bash
   docker compose up -d
   ```
3. **Check it.** `docker compose ps` shows `healthy` after about a minute, and `docker compose logs -f` shows `Configuration validated successfully`.

> [!NOTE]
> If you also run the **ITSD Classifier** with its built-in reminder enabled (`REMINDER_ENABLED=true`), don't run this bot as well. Every thread would be reminded twice.

---

## ✨ Features

| | Feature | What it does |
|---|---|---|
| 🔍 | Watches one channel | Reads today's top-level messages from the channel you name, every `CHECK_INTERVAL_HOURS` hours |
| ⏰ | Waits before it nags | Only reminds when a message is older than `AGE_THRESHOLD_SECONDS`, so people get time to pick a category |
| 🤖 | Respects the HelpDesk bot | Skips any thread the HelpDesk bot (`HELPDESK_BOT_ID`) has already replied to |
| 🔄 | Never reminds twice | Skips threads where its own bot user already replied (matched on user ID, so changing `REMINDER_MESSAGE` never breaks it) and keeps a JSON log of reminded threads |
| 📜 | Covers busy days | Follows `conversations.history` pagination, so days beyond 200 messages are covered |
| ✏️ | Your wording | `REMINDER_MESSAGE` sets the text; `{user}` becomes the author's mention |
| ❤️ | Real health check | The loop touches a heartbeat file; the container is unhealthy if it goes stale |
| 🐳 | Docker ready | Image builds for Intel and Apple Silicon; compose file sets resource limits and log rotation |
| 🔒 | Locked down | Non-root user, hash-pinned dependencies, Debian security updates at build time, credentials only in environment variables |

---

## 🗺️ Architecture

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/architecture-dark.svg">
  <img src="docs/assets/architecture-light.svg" width="100%"
       alt="The reminder bot runs in one Docker container configured from .env; it reads channel history and thread replies from Slack, posts reminders with chat.postMessage, keeps a log of handled threads on the ./data volume, and touches a heartbeat file that the Docker health check reads.">
</picture>

Each check, end to end:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/reminder-loop-dark.svg">
  <img src="docs/assets/reminder-loop-light.svg" width="100%"
       alt="Each check fetches today's channel messages, keeps top-level human messages older than the age threshold that are not yet logged, and asks whether the HelpDesk bot or this bot already replied. If not, it posts a reminder in the thread. Either way the thread is logged, then the bot sleeps until the next check.">
</picture>

[docs/how-it-works.md](docs/how-it-works.md) has the details, including what the bot does not cover.

---

## 🧭 Supported and tested

| Item | Status |
|---|---|
| Python 3.13 | Pinned in the Dockerfile and in CI, which runs ruff, pytest and the diagram check |
| Python 3.14 | `make check` passes on macOS |
| Docker image | Builds and runs on Docker 29 on macOS (Apple Silicon) |
| Linux hosts, Intel image | Unverified here |
| Slack | Public channels. Private channels, Enterprise Grid and Slack Connect channels are unverified |
| Live workspace | The Slack client is mocked in the test suite. A run against a real workspace is unverified in this repository's checks |

Ran it somewhere not on this list? See [Contributing](#-contributing).

---

## ⚙️ Configuration

Copy [.env.example](.env.example) to `.env`. Never commit `.env`.

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `SLACK_BOT_TOKEN` | Yes | none | Bot User OAuth token, starts with `xoxb-` |
| `CHANNEL_ID` | Yes | none | ID of the channel to monitor |
| `HELPDESK_BOT_ID` | Yes | none | Bot ID of the HelpDesk bot whose reply means "handled" |
| `AGE_THRESHOLD_SECONDS` | No | `10800` | Age a message must reach before a reminder (3 hours) |
| `CHECK_INTERVAL_HOURS` | No | `2` | Hours between checks |
| `REMINDER_LOG_FILE` | No | `/app/data/reminded_messages.json` | JSON file of already-reminded threads |
| `REMINDER_MESSAGE` | No | Built-in message | Reminder text; `{user}` is replaced with the author's mention |
| `HEARTBEAT_FILE` | No | `/tmp/itsd-reminder.heartbeat` | File the loop touches; the health check fails if it is older than 30 minutes |

The container's health check reads `/tmp/itsd-reminder.heartbeat`, so leave `HEARTBEAT_FILE` alone when you run in Docker.

---

## 📖 Usage

Day to day, run it through Compose:

```bash
docker compose logs -f          # follow the log
docker compose down             # stop
docker compose up -d --build    # rebuild after code changes
```

To run it without Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install --require-hashes -r requirements.lock.txt
export SLACK_BOT_TOKEN="xoxb-your-token"
export CHANNEL_ID="C0XXXXXXXXX"
export HELPDESK_BOT_ID="B0XXXXXXXXX"
python src/main.py
```

Outside Docker, set `REMINDER_LOG_FILE` to a path you can write, because the default is `/app/data/reminded_messages.json`.

---

## 📁 Repo structure

```text
ITSD-Reminder/
├── src/
│   ├── __init__.py
│   └── main.py               # 🧠 bot loop: fetch, filter, remind, log
├── tests/
│   ├── test_main.py          # 🧪 pytest suite (Slack mocked)
│   └── test_diagrams.py      # 🖼️ committed SVGs match the generator
├── tools/
│   ├── gen_diagram.py        # 🖌️ draws the diagrams (stdlib only)
│   └── brand/                # 🎨 icon and social preview generator, icon freshness check
├── docs/
│   ├── README.md             # 🗺️ docs index
│   ├── setup.md              # 🧭 Slack app, IDs, install
│   ├── how-it-works.md       # ⚙️ one check, step by step
│   ├── troubleshooting.md    # 🛠️ symptoms and fixes
│   ├── faq.md                # ❓ short answers
│   └── assets/               # 🖼️ diagrams, brand icon, social preview
├── .github/                  # 🤖 CI workflow (make check) and dependabot config
├── Makefile                  # 🔧 venv, lint, test, diagram, check, social-preview
├── .env.example              # ⚙️ template, copy to .env (gitignored)
├── Dockerfile                # 🐳 multi-arch image, non-root user
├── docker-compose.yml        # 🐳 service, ./data volume, health check
├── requirements.txt          # 📦 direct dependencies
├── requirements.lock.txt     # 🔒 hash-pinned lockfile
├── llms.txt                  # 🔎 plain-text project summary
├── AGENTS.md                 # 🤝 notes for contributors and coding agents
├── README.md  CONTRIBUTING.md  SECURITY.md  LICENSE
└── .gitignore  .dockerignore
```

Runtime state (`data/reminded_messages.json`) is written to the gitignored `./data` volume.

---

## 🧪 Testing

```bash
make venv     # once: .venv with the locked dependencies, pytest and ruff
make check    # ruff, pytest and the diagram check, as CI runs them
```

`tests/test_diagrams.py` checks that the committed SVGs in `docs/assets/` match `tools/gen_diagram.py`. Run `make diagram` after changing a diagram.

---

## 📦 Deployment

```bash
docker compose up -d
```

The image supports Intel/AMD64 and Apple Silicon (ARM64). State lives in `./data`, mounted at `/app/data`. The compose file limits the container to 0.5 CPU and 256 MB and rotates its logs at 10 MB, three files.

---

## 🛠️ Troubleshooting

Symptoms and fixes are in [docs/troubleshooting.md](docs/troubleshooting.md). The short list:

| Symptom | First thing to check |
|---|---|
| Container exits at start | The three required variables are set in `.env` |
| `channel_not_found` in the log | `CHANNEL_ID` is right and the bot is invited to the channel |
| No reminders appear | The message is older than `AGE_THRESHOLD_SECONDS`, was posted today (UTC), and has no HelpDesk bot reply |
| Container shows `unhealthy` | The loop has stopped touching the heartbeat; read `docker compose logs` |

---

## 🔒 Security

The bot token lives only in `.env`, which is gitignored. The container runs as a non-root user with hash-pinned dependencies. See [SECURITY.md](SECURITY.md) to report a vulnerability.

---

## 🤝 Contributing

Bug reports and environment reports are welcome. Open an issue and include:

- Your OS, Docker version, and whether you ran in Docker or with Python directly
- The last 50 lines of `docker compose logs` with the token removed
- Your `AGE_THRESHOLD_SECONDS` and `CHECK_INTERVAL_HOURS`
- The Slack error name if there is one, such as `channel_not_found`

To report a Slack setup that works and is not in the table above (a private channel, an Enterprise Grid workspace), say what you ran and what happened. Pull requests follow [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT. See [LICENSE](LICENSE).

---

<p align="center"><sub>Made with ❤️ by <a href="https://github.com/CaputoDavide93">Davide Caputo</a></sub></p>
