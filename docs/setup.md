# 🧭 Setup

This takes about ten minutes if you can create Slack apps in your workspace. There is no UI in this project to screenshot, so each step names the Slack screen to use.

## Before you start

- Docker 20.10 or newer with Compose 2 (or Python 3.13 to run without Docker)
- Permission to create and install a Slack app in your workspace
- The Service Desk channel, public, where tickets are posted
- A HelpDesk bot that replies in a ticket's thread once it has processed the ticket

## 1. Create the Slack app

1. Open [api.slack.com/apps](https://api.slack.com/apps), choose **Create New App**, then **From scratch**.
2. Name it, for example `ITSD Reminder Bot`, and pick your workspace.
3. Open **OAuth & Permissions** and add these **Bot Token Scopes**:

| Scope | Why |
|---|---|
| `channels:history` | Read messages and thread replies in public channels |
| `chat:write` | Post the reminder |
| `channels:read` | Listed in the original setup guide; the code does not call a method that needs it |
| `users:read` | Listed in the original setup guide; the code does not call a method that needs it |

4. Choose **Install to Workspace** and allow it.
5. Copy the **Bot User OAuth Token**. It starts with `xoxb-`. This is `SLACK_BOT_TOKEN`.

## 2. Invite the bot to the channel

In the Service Desk channel, type `/invite @YourBotName`.

## 3. Find the two IDs

- **`CHANNEL_ID`:** right-click the channel, **View channel details**, and copy the Channel ID at the bottom. It starts with `C`.
- **`HELPDESK_BOT_ID`:** the `bot_id` carried by the HelpDesk bot's messages. It starts with `B`. Slack's message menus do not show it, so read it from the API: call [`conversations.history`](https://api.slack.com/methods/conversations.history) for the channel (the API tester on api.slack.com works) and copy `bot_id` from one of the HelpDesk bot's messages.

The bot compares `bot_id` on thread replies with `HELPDESK_BOT_ID`. A user ID (starts with `U`) or an app ID (starts with `A`) will not match.

## 4. Install

```bash
git clone https://github.com/CaputoDavide93/ITSD-Reminder.git
cd ITSD-Reminder
cp .env.example .env
nano .env
docker compose up -d
```

In `.env`, set `SLACK_BOT_TOKEN`, `CHANNEL_ID` and `HELPDESK_BOT_ID`. Everything else has a default; see the [configuration table](../README.md#️-configuration).

## 5. Check it works

```bash
docker compose ps
docker compose logs -f
```

- `docker compose ps` shows `healthy` after about a minute.
- The log starts with `Configuration validated successfully`, then `Running reminder check at ...`.
- `Slack API Error: invalid_auth` means the token is wrong or not the Bot User OAuth token.

To see a reminder, post a message in the channel as a person (not through the HelpDesk bot), wait past `AGE_THRESHOLD_SECONDS` and the next check. To test faster, set `AGE_THRESHOLD_SECONDS=60` and `CHECK_INTERVAL_HOURS=0.05`, then run `docker compose up -d` again.

## Changing settings later

Edit `.env`, then run `docker compose up -d` so Compose recreates the container with the new values.

## Stopping

```bash
docker compose down
```

The reminded-thread log stays in `./data`.
