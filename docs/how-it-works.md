# ⚙️ How it works

The bot is one Python loop in `src/main.py`. It calls the Slack Web API and keeps two small pieces of state: a JSON log of reminded threads and a heartbeat file.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/architecture-dark.svg">
  <img src="assets/architecture-light.svg" width="100%" alt="The bot runs in one Docker container, reads channel history and replies from Slack, posts reminders, keeps a log on the data volume and touches a heartbeat file.">
</picture>

## One check

Every `CHECK_INTERVAL_HOURS` hours (default 2) the bot runs these steps.

1. **Fetch today's messages.** It reads the channel history from 00:00 UTC today, following Slack's pagination cursor until it has everything.
2. **Drop what it should ignore.** A message is skipped if it came from a bot (`bot_message` subtype or a `bot_id`), has no `user`, is a reply inside a thread, is younger than `AGE_THRESHOLD_SECONDS`, or is already in the log.
3. **Read the thread.** For each remaining message it fetches the thread's replies.
4. **Decide.** If any reply has `bot_id` equal to `HELPDESK_BOT_ID`, the ticket counts as handled. If any reply came from the bot's own user ID, it was already reminded. Either way the thread goes into the log and nothing is posted.
5. **Remind.** Otherwise it posts `REMINDER_MESSAGE` in the thread, with `{user}` replaced by the author's ID, and logs the thread.
6. **Save the log.** The set of reminded thread timestamps is written to `REMINDER_LOG_FILE` at the end of the check.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/reminder-loop-dark.svg">
  <img src="assets/reminder-loop-light.svg" width="100%" alt="Fetch today's messages, filter, read the thread, post a reminder unless the HelpDesk bot or this bot already replied, log the thread, sleep.">
</picture>

## Two duplicate checks

The bot looks for its own earlier reply by user ID, so changing the reminder wording never makes it forget old reminders. The JSON log skips the thread fetch for threads already handled, which saves one Slack call per thread on later checks.

## The log

`data/reminded_messages.json` is a JSON array of Slack message timestamps. Deleting it is safe: the next check rebuilds the same decisions from thread replies, because the bot's own earlier reply is still there.

## The health check

The loop touches `HEARTBEAT_FILE` at the start of each check and every 15 minutes while it waits. The Dockerfile and `docker-compose.yml` mark the container unhealthy when the file is older than 30 minutes, which catches a loop stuck on a hung call.

## What it does not cover

- **Only today, in UTC.** Messages from earlier days are never fetched. A ticket posted late in the evening UTC, whose threshold ends after midnight UTC, is not reminded.
- **One channel.** Set by `CHANNEL_ID`.
- **No category check.** The bot never reads a ticket's category. It treats the HelpDesk bot's reply as the signal that the ticket was processed.
- **One reminder per ticket.** There is no second nudge.
- **Slack errors.** `cannot_reply_to_message` is logged and the thread is marked done. Other posting errors are logged and the thread is tried again at the next check.
