# ❓ FAQ

## What does ITSD Reminder do?

It replies in a Slack thread to remind the author of an IT Service Desk ticket to pick a category. It does this when the message is older than a threshold and the HelpDesk bot has not replied to it. It reminds each ticket once.

## How does it know a category is missing?

It does not read categories. It checks whether the HelpDesk bot (`HELPDESK_BOT_ID`) has replied in the ticket's thread, and treats a missing reply as an unprocessed ticket. This fits setups where that bot replies to every ticket it processes.

## Will it remind the same ticket twice?

No. It skips any thread where its own bot user already replied, and it keeps a JSON log of reminded threads. Changing `REMINDER_MESSAGE` does not break this, because the check uses the user ID, not the text.

## How long does it wait before reminding?

3 hours by default. Set `AGE_THRESHOLD_SECONDS` to change it, for example `7200` for 2 hours. It checks every 2 hours by default, so a reminder can arrive up to one check interval after the threshold passes. Set `CHECK_INTERVAL_HOURS` to change that.

## Can I change the reminder text?

Yes. Set `REMINDER_MESSAGE` in `.env`. Use `{user}` where the author's mention should go, for example `Hi <@{user}>, please pick a category for this ticket.`

## Does it work in a private channel?

Unverified. The setup guide uses public-channel scopes (`channels:history`), and the tested path is a public channel. Private channels use different Slack scopes and have not been tested here.

## Does it work with other help desk tools?

It works with any setup where a bot replies in the thread once a ticket is processed. Set `HELPDESK_BOT_ID` to that bot's `bot_id`. Setups that do not post a bot reply are not supported.

## Does it remind about tickets from yesterday?

No. It reads messages posted since 00:00 UTC today. See [what it does not cover](how-it-works.md#what-it-does-not-cover).

## Can it watch more than one channel?

Not in one container. Run a second copy with its own `.env`, `CHANNEL_ID` and data directory.

## Where does it store data?

In `./data/reminded_messages.json` on the host, mounted at `/app/data`. It holds Slack message timestamps and nothing else. The bot token stays in `.env`.

## Is it safe to run?

The container runs as a non-root user, installs hash-pinned dependencies and takes credentials only from environment variables. To report a vulnerability, follow [SECURITY.md](../SECURITY.md).

## What does it cost?

Nothing. It is MIT licensed, and it uses the Slack Web API with your own app.
