import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# === CONFIGURATION (loaded from environment variables) ===
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
AGE_THRESHOLD_SECONDS = int(os.environ.get("AGE_THRESHOLD_SECONDS", "10800"))  # Default: 3 hours
REMINDER_LOG_FILE = os.environ.get("REMINDER_LOG_FILE", "/app/data/reminded_messages.json")
HELPDESK_BOT_ID = os.environ.get("HELPDESK_BOT_ID")
CHECK_INTERVAL_HOURS = float(os.environ.get("CHECK_INTERVAL_HOURS", "2"))  # Default: 2 hours
HEARTBEAT_FILE = os.environ.get("HEARTBEAT_FILE", "/tmp/itsd-reminder.heartbeat")
REMINDER_MESSAGE = os.environ.get(
    "REMINDER_MESSAGE",
    "👋 Hi <@{user}>, you've started a ticket but forgot the category! Help us help you, select one to get things moving."
)


def validate_config():
    """Validate required configuration is present."""
    missing = []
    if not SLACK_BOT_TOKEN:
        missing.append("SLACK_BOT_TOKEN")
    if not CHANNEL_ID:
        missing.append("CHANNEL_ID")
    if not HELPDESK_BOT_ID:
        missing.append("HELPDESK_BOT_ID")
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please set them in your .env file or environment.")
        sys.exit(1)
    
    print("✅ Configuration validated successfully")


# Validate config on startup
validate_config()

client = WebClient(token=SLACK_BOT_TOKEN)

_bot_user_id = None


def get_bot_user_id():
    """Our own bot user ID, used to spot reminders we already posted
    (matching on message text broke whenever REMINDER_MESSAGE changed)."""
    global _bot_user_id
    if _bot_user_id is None:
        _bot_user_id = client.auth_test()["user_id"]
    return _bot_user_id


def touch_heartbeat():
    """Container HEALTHCHECK checks this file's age."""
    try:
        with open(HEARTBEAT_FILE, "a"):
            os.utime(HEARTBEAT_FILE, None)
    except OSError as e:
        print(f"Could not update heartbeat file {HEARTBEAT_FILE}: {e}")


def fetch_history(oldest):
    """All top-level channel messages since `oldest`, following pagination."""
    messages, cursor = [], None
    while True:
        kwargs = {"channel": CHANNEL_ID, "oldest": str(oldest), "limit": 200}
        if cursor:
            kwargs["cursor"] = cursor
        response = client.conversations_history(**kwargs)
        messages.extend(response["messages"])
        cursor = (response.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return messages


def get_today_start_unix():
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return today_start.timestamp()


def get_cutoff_unix(seconds_ago=AGE_THRESHOLD_SECONDS):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).timestamp()


def load_reminded_messages():
    if not os.path.exists(REMINDER_LOG_FILE):
        return set()
    with open(REMINDER_LOG_FILE, "r") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()


def save_reminded_messages(reminded):
    with open(REMINDER_LOG_FILE, "w") as f:
        json.dump(list(reminded), f)


def check_and_remind():
    today_start = get_today_start_unix()
    cutoff_time = get_cutoff_unix()
    reminded = load_reminded_messages()

    try:
        bot_user_id = get_bot_user_id()

        for message in fetch_history(today_start):
            ts = float(message["ts"])
            thread_ts = message["ts"]

            # Skip bot messages or replies
            if "subtype" in message and message["subtype"] == "bot_message":
                continue
            if "bot_id" in message or "user" not in message:
                continue
            if "thread_ts" in message and message["thread_ts"] != message["ts"]:
                continue
            if ts > cutoff_time:
                continue
            if thread_ts in reminded:
                continue

            user = message["user"]

            # Get replies to check for HelpDesk or prior reminders
            try:
                replies = client.conversations_replies(channel=CHANNEL_ID, ts=thread_ts)
            except SlackApiError as e:
                print(f"Failed to fetch replies for {thread_ts}: {e.response['error']}")
                continue

            helpdesk_found = any(
                reply.get("bot_id") == HELPDESK_BOT_ID
                for reply in replies["messages"]
                if reply.get("ts") != thread_ts
            )

            already_reminded = any(
                reply.get("user") == bot_user_id
                for reply in replies["messages"]
                if reply.get("ts") != thread_ts
            )

            if helpdesk_found or already_reminded:
                reminded.add(thread_ts)
                continue

            print(f"⏰ Sending reminder for thread: {thread_ts}")
            try:
                client.chat_postMessage(
                    channel=CHANNEL_ID,
                    thread_ts=thread_ts,
                    text=REMINDER_MESSAGE.format(user=user)
                )
                reminded.add(thread_ts)
            except SlackApiError as e:
                print(f"Slack API Error on message {thread_ts}: {e.response['error']}")
                if e.response['error'] == "cannot_reply_to_message":
                    reminded.add(thread_ts)  # Prevent retrying

        save_reminded_messages(reminded)

    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")


if __name__ == "__main__":
    print("🤖 ITSD Reminder Bot starting...")
    print(f"📺 Monitoring channel: {CHANNEL_ID}")
    print(f"⏰ Age threshold: {AGE_THRESHOLD_SECONDS} seconds")
    print(f"🔄 Check interval: {CHECK_INTERVAL_HOURS} hours")
    
    while True:
        print(f"\n🚀 Running reminder check at {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')}")
        touch_heartbeat()
        check_and_remind()

        total_wait = int(CHECK_INTERVAL_HOURS * 60 * 60)  # Convert hours to seconds
        interval = 15 * 60  # 15 minutes in seconds
        elapsed = 0

        while elapsed < total_wait:
            time.sleep(interval)
            elapsed += interval
            touch_heartbeat()
            remaining = total_wait - elapsed
            mins = remaining // 60
            print(f"⏳ Next run in {mins} minutes... ({datetime.now().astimezone().strftime('%H:%M:%S')})")
