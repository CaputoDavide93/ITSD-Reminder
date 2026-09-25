"""Dedup and pagination behaviour of the reminder loop (Slack client mocked)."""

import importlib
import os
import sys
import time
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture
def bot(tmp_path, monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("CHANNEL_ID", "C1")
    monkeypatch.setenv("HELPDESK_BOT_ID", "BHELP")
    monkeypatch.setenv("REMINDER_LOG_FILE", str(tmp_path / "reminded.json"))
    monkeypatch.setenv("HEARTBEAT_FILE", str(tmp_path / "hb"))
    import main
    main = importlib.reload(main)
    main.client = mock.Mock()
    main.client.auth_test.return_value = {"user_id": "UBOT"}
    return main


def old_ts():
    return str(time.time() - 4 * 3600)


def test_existing_reminder_by_bot_user_is_not_repeated(bot):
    ts = old_ts()
    bot.client.conversations_history.return_value = {"messages": [{"ts": ts, "user": "U1"}]}
    bot.client.conversations_replies.return_value = {"messages": [
        {"ts": ts, "user": "U1"},
        {"ts": "2", "user": "UBOT", "text": "any wording at all"},
    ]}
    bot.check_and_remind()
    bot.client.chat_postMessage.assert_not_called()


def test_reminds_when_no_helpdesk_or_bot_reply(bot):
    ts = old_ts()
    bot.client.conversations_history.return_value = {"messages": [{"ts": ts, "user": "U1"}]}
    bot.client.conversations_replies.return_value = {"messages": [{"ts": ts, "user": "U1"}]}
    bot.check_and_remind()
    bot.client.chat_postMessage.assert_called_once()


def test_history_is_paginated(bot):
    bot.client.conversations_history.side_effect = [
        {"messages": [{"ts": "1"}], "response_metadata": {"next_cursor": "abc"}},
        {"messages": [{"ts": "2"}], "response_metadata": {"next_cursor": ""}},
    ]
    assert [m["ts"] for m in bot.fetch_history(0)] == ["1", "2"]
    assert bot.client.conversations_history.call_args_list[1].kwargs["cursor"] == "abc"


def test_heartbeat_touched(bot):
    bot.touch_heartbeat()
    assert time.time() - os.path.getmtime(bot.HEARTBEAT_FILE) < 5
