import pytest

import database
from agent import SupportChatbot
from fake_model import FakeModel
from fallback_model import FallbackModel
from keyword_model import KeywordModel
from tools import CrescentTools


class SilentModel:
    def decide(self, instructions, history, tools):
        return None


def make_bot(tmp_path, model):
    db = tmp_path / "test.db"
    database.create_tables(db)
    return SupportChatbot("Crescent", "Use tool facts.", CrescentTools(db), model)


def test_model_lookup_answers_from_database(tmp_path):
    model = FakeModel(
        [
            {"tool": "look_up_estimate", "arguments": {"estimate_id": "E101"}},
            {"text": "Example E101 is $3,900.00 monthly."},
        ]
    )
    bot = make_bot(tmp_path, model)
    bot.respond("What is example E101?")
    assert "$3,900.00" in bot.history[1]["content"]


def test_made_up_amount_never_reaches_database(tmp_path):
    model = FakeModel(
        [
            {
                "tool": "request_down_payment_change",
                "arguments": {"estimate_id": "E101", "new_down_payment": "100000"},
            },
            {"text": "What is the new amount?"},
        ]
    )
    bot = make_bot(tmp_path, model)
    bot.respond("Change example E101")
    assert database.waiting_requests(bot.tools.db_file) == []


@pytest.mark.parametrize(
    "text",
    [
        "Do I qualify?",
        "Is this halal?",
        "SSN 123-45-6789",
        "123456789",
        "123 45 6789",
        "financial advice please",
    ],
)
def test_handoff_never_reaches_model_or_history(tmp_path, text):
    model = FakeModel([])
    bot = make_bot(tmp_path, model)
    assert "human" in bot.respond(text)
    assert model.calls == 0
    assert bot.history == []


def test_offline_fallback_lookup(tmp_path):
    bot = make_bot(tmp_path, FallbackModel(SilentModel(), KeywordModel()))
    assert "$3,900.00" in bot.respond("What is estimate E101?")
    assert "120 months" in bot.respond("What is plan P10?")


def test_valid_model_change_waits(tmp_path):
    bot = make_bot(
        tmp_path,
        FakeModel(
            [
                {
                    "tool": "request_down_payment_change",
                    "arguments": {"estimate_id": "E101", "new_down_payment": "100000"},
                },
                {"text": "Request sent to staff."},
            ]
        ),
    )
    bot.respond("Change E101 to $100,000 down.")
    assert len(database.waiting_requests(bot.tools.db_file)) == 1
    assert database.find_estimate(bot.tools.db_file, "E101")["down_payment"] == 90000
