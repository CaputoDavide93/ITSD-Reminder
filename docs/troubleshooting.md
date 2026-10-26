# 🛠️ Troubleshooting

Start with `docker compose ps` and `docker compose logs -f`. Remove the token before pasting a log anywhere.

## The container exits straight away

The log says `Missing required environment variables: ...`. Set `SLACK_BOT_TOKEN`, `CHANNEL_ID` and `HELPDESK_BOT_ID` in `.env`, then run `docker compose up -d`. The bot refuses to start without all three.

## `Slack API Error: invalid_auth`

The token is wrong. Use the **Bot User OAuth Token** (starts with `xoxb-`) from **OAuth & Permissions**, and reinstall the app if you changed its scopes.

## `Slack API Error: channel_not_found`

Either `CHANNEL_ID` is wrong or the bot is not in the channel. Copy the ID again from **View channel details** and run `/invite @YourBotName` in the channel. Private channels are unverified; see the [FAQ](faq.md#does-it-work-in-a-private-channel).

## `Slack API Error: missing_scope`

The app lacks a permission. Add `channels:history` and `chat:write`, reinstall the app, and copy the new token if Slack issues one.

## No reminders appear

Work down this list. A message is reminded only when all of these hold:

1. It was posted today, in UTC.
2. It is a top-level message from a person, not a bot and not a reply.
3. It is older than `AGE_THRESHOLD_SECONDS` (default 3 hours).
4. The HelpDesk bot has not replied in its thread, and this bot has not either.
5. The next check has run. Checks happen every `CHECK_INTERVAL_HOURS` (default 2).

If the HelpDesk bot replies to every ticket the moment it is posted, the bot has nothing to remind. If `HELPDESK_BOT_ID` does not match, see the next item.

## Reminders on tickets that are already handled

`HELPDESK_BOT_ID` does not match the `bot_id` on the HelpDesk bot's replies. Read a reply from `conversations.history` and copy its `bot_id`.

## Everyone gets reminded twice

Another reminder is running, for example the ITSD Classifier with `REMINDER_ENABLED=true`. Run only one.

## The container is `unhealthy`

The heartbeat file is older than 30 minutes, so the loop is stuck or has crashed. Read `docker compose logs` for the last line before it went quiet. If you set `HEARTBEAT_FILE` to a different path, the health check cannot see it, because the Dockerfile and compose file read `/tmp/itsd-reminder.heartbeat`. Unset it.

## `PermissionError` writing the log (Linux hosts)

The container runs as user 1000. If Docker created `./data` as root, the bot cannot write `reminded_messages.json`. Fix it with:

```bash
mkdir -p data && sudo chown 1000:1000 data
docker compose up -d
```

This is unverified here, since the tested host was macOS, where Docker Desktop handles the mount.

## Reminded threads are forgotten after a restart

`./data` is not mounted or is not writable. Check that `docker-compose.yml` still has `./data:/app/data` under `volumes`. The bot also recognises its own earlier replies, so a lost log does not cause duplicate reminders by itself.

## Still stuck

Open an issue with the details listed under [Contributing](../README.md#-contributing).
