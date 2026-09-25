<div align="center">

# 🤖 ITSD Reminder Bot

**A Slack bot that reminds people to pick a category when they open an IT Service Desk ticket without one**

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Slack](https://img.shields.io/badge/Slack-Web%20API-4A154B?logo=slack&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
[![CI](https://github.com/CaputoDavide93/ITSD-Reminder/actions/workflows/ci.yml/badge.svg)](https://github.com/CaputoDavide93/ITSD-Reminder/actions/workflows/ci.yml)

[Features](#-features) • [Architecture](#️-architecture) • [Quick Start](#-quick-start) • [Configuration](#️-configuration) • [Testing](#-testing) • [Contributing](#-contributing)

</div>

---

The bot watches your IT Service Desk channel and, when someone opens a ticket and forgets to select a category, replies in the thread to remind them.

> [!NOTE]
> If you also run the **ITSD Classifier** with its built-in reminder enabled (`REMINDER_ENABLED=true`), don't run this bot as well — every thread would be reminded twice.

---

## ✨ Features

| | Feature | What it does |
|---|---|---|
| 🔍 | Automatic Monitoring | Continuously monitors your Slack channel for new tickets |
| ⏰ | Smart Timing | Only reminds users after a configurable time threshold |
| 🤖 | HelpDesk Integration | Detects when HelpDesk bot has already processed a ticket |
| 🔄 | Duplicate Prevention | Skips threads our own bot already replied to (matched on bot user ID, so changing `REMINDER_MESSAGE` never breaks it) plus a JSON log of reminded threads |
| 📜 | Full History | Follows `conversations.history` pagination, so busy days beyond 200 messages are covered |
| ❤️ | Real Health Check | The loop touches a heartbeat file; the container is unhealthy if it goes stale |
| 🐳 | Docker Ready | Fully containerized with multi-architecture support (Intel & Apple Silicon) |
| 🔒 | Secure | Non-root user, hash-pinned dependencies, Debian security updates at build time, credentials via environment variables |

---

## 🗺️ Architecture

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/architecture-dark.svg">
  <img src="docs/assets/architecture-light.svg" width="100%"
       alt="The reminder bot runs in one Docker container configured from .env. It reads the service desk channel and posts reminders through the Slack Web API, keeps a log of reminded threads on the ./data volume, and touches a heartbeat file that the Docker health check watches.">
</picture>

Each check, end to end:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/reminder-loop-dark.svg">
  <img src="docs/assets/reminder-loop-light.svg" width="100%"
       alt="Each check fetches today's channel messages, keeps top-level human messages older than the age threshold that are not yet logged, and asks whether the HelpDesk bot or this bot already replied. If not, it posts a reminder in the thread. Either way the thread is logged, then the bot sleeps until the next check.">
</picture>

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/CaputoDavide93/ITSD-Reminder.git
cd ITSD-Reminder

# Configure environment
cp .env.example .env
nano .env  # Add your Slack credentials

# Run with Docker
docker compose up -d
```

---

## 📋 Prerequisites

### For Docker Deployment (Recommended)

| Requirement | Version |
|-------------|---------|
| 🐳 Docker | 20.10+ |
| 📦 Docker Compose | 2.0+ |

### For Local Development

| Requirement | Version |
|-------------|---------|
| 🐍 Python | 3.13 |
| 📦 pip | Latest |

### Slack Bot Setup

<details>
<summary><strong>📋 Step-by-Step Guide</strong></summary>

#### Step 1: Create a Slack App
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Enter an App Name (e.g., "ITSD Reminder Bot")
4. Select your workspace and click "Create App"

#### Step 2: Configure Bot Permissions
1. Navigate to "OAuth & Permissions"
2. Add these **Bot Token Scopes**:

| Scope | Purpose |
|-------|---------|
| `channels:history` | Read messages from public channels |
| `channels:read` | View basic channel info |
| `chat:write` | Send reminder messages |
| `users:read` | Get user information for mentions |

#### Step 3: Install the App
1. Click "Install to Workspace"
2. Review permissions and click "Allow"
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

#### Step 4: Invite Bot to Channel
1. Open your IT Service Desk channel in Slack
2. Type `/invite @YourBotName`

</details>

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `SLACK_BOT_TOKEN` | ✅ | - | Your Slack Bot OAuth Token |
| `CHANNEL_ID` | ✅ | - | The Slack channel ID to monitor |
| `HELPDESK_BOT_ID` | ✅ | - | The HelpDesk bot's ID |
| `AGE_THRESHOLD_SECONDS` | ❌ | `10800` | Time to wait before sending reminder (3 hours) |
| `CHECK_INTERVAL_HOURS` | ❌ | `2` | How often to check for new messages |
| `REMINDER_LOG_FILE` | ❌ | `/app/data/reminded_messages.json` | Path of the JSON file tracking already-reminded threads |
| `REMINDER_MESSAGE` | ❌ | Built-in message | Custom reminder text — `{user}` is replaced with the ticket author's mention |
| `HEARTBEAT_FILE` | ❌ | `/tmp/itsd-reminder.heartbeat` | File touched by the loop; the health check fails if it is older than 30 min |

### Example Configuration

```bash
# .env
SLACK_BOT_TOKEN=xoxb-your-token-here
CHANNEL_ID=C0XXXXXXXXX
HELPDESK_BOT_ID=B0XXXXXXXXX
AGE_THRESHOLD_SECONDS=10800
CHECK_INTERVAL_HOURS=2
# REMINDER_LOG_FILE=/app/data/reminded_messages.json
# REMINDER_MESSAGE=👋 Hi <@{user}>, you've started a ticket but forgot the category! Help us help you, select one to get things moving.
```

> ⚠️ **Security Note**: Never commit your `.env` file to version control!

---

## 📖 Usage

Run the bot outside Docker:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (hash-pinned)
pip install --require-hashes -r requirements.lock.txt

# Set environment variables
export SLACK_BOT_TOKEN="xoxb-your-token"
export CHANNEL_ID="C0XXXXXXXXX"
export HELPDESK_BOT_ID="B0XXXXXXXXX"

# Run the bot
python src/main.py
```

---

## 📁 Repo structure

```text
ITSD-Reminder/
├── src/
│   ├── __init__.py
│   └── main.py              # 🧠 bot loop: fetch, filter, remind, log
├── tests/
│   ├── test_main.py         # 🧪 pytest suite (Slack mocked)
│   └── test_diagrams.py     # 🖼️ committed SVGs match the generator
├── tools/
│   └── gen_diagram.py       # 🖌️ draws the README diagrams (stdlib only)
├── docs/assets/             # 🗺️ diagram SVGs, light + dark
├── .github/workflows/ci.yml # 🤖 ruff + pytest on push and PR
├── .env.example             # ⚙️ template, copy to .env (gitignored)
├── Dockerfile               # 🐳 multi-arch image, non-root user
├── docker-compose.yml       # 🐳 service, ./data volume, health check
├── requirements.txt         # 📦 direct dependencies
├── requirements.lock.txt    # 🔒 hash-pinned lockfile (uv pip compile)
├── .gitignore  .dockerignore
├── README.md  CONTRIBUTING.md  SECURITY.md  # 📄 community files
└── LICENSE                  # 📄 MIT
```

Runtime state (`data/reminded_messages.json`) is written to the gitignored `./data` volume.

---

## 🧪 Testing

```bash
pip install pytest ruff
pytest -q tests      # Slack client is mocked
ruff check src tests
```

CI ([ci.yml](.github/workflows/ci.yml)) runs both on every push and pull request. `tests/test_diagrams.py` also checks that the committed SVGs in `docs/assets/` match `tools/gen_diagram.py`; run `python3 tools/gen_diagram.py` after changing a diagram.

---

## 📦 Deployment

### Multi-Architecture Support

This image supports both Intel/AMD64 and Apple Silicon (ARM64).

### Docker Compose

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

---

## 🛠️ Troubleshooting

<details>
<summary><strong>❌ Bot not responding</strong></summary>

- Check if the bot is running and healthy: `docker compose ps`
- Verify logs for errors: `docker compose logs -f`
- Ensure environment variables are set correctly
</details>

<details>
<summary><strong>❌ "channel_not_found" error</strong></summary>

- Verify the `CHANNEL_ID` is correct
- Ensure the bot is invited to the channel: `/invite @YourBotName`
</details>

<details>
<summary><strong>❌ Messages not being detected</strong></summary>

- Check `AGE_THRESHOLD_SECONDS` - messages must be older than this value
- Verify the bot has `channels:history` permission
</details>

---

## 🔒 Security

The bot token lives only in `.env`, which is gitignored. The container runs as a non-root user with hash-pinned dependencies. See [SECURITY.md](SECURITY.md) to report a vulnerability.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔃 Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>⭐ If this project helped you, please give it a star! ⭐</sub>
  <br>
  <sub>Made with ❤️ by <a href="https://github.com/CaputoDavide93">Davide Caputo</a></sub>
</p>
