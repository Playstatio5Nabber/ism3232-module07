import pytest

import database
from tools import CrescentTools


def make_tools(tmp_path):
    db = tmp_path / "test.db"
    database.create_tables(db)
    return CrescentTools(db)


def customer(text):
    return [{"role": "user", "content": text}]


def test_lookup_finds_id_in_sentence(tmp_path):
    tools = make_tools(tmp_path)
    text = "What is example E101?"
    assert "$3,900.00" in tools.run(
        "look_up_estimate", {"estimate_id": text}, customer(text)
    )
    assert "120 months" in tools.run(
        "look_up_plan", {"plan_id": "P10"}, customer("Plan P10?")
    )


def test_change_waits(tmp_path):
    tools = make_tools(tmp_path)
    reply = tools.run(
        "request_down_payment_change",
        {"estimate_id": "E101", "new_down_payment": "100000"},
        customer("Change E101 to $100,000."),
    )
    assert "has not changed yet" in reply
    assert database.find_estimate(tools.db_file, "E101")["down_payment"] == 90000
    assert len(database.waiting_requests(tools.db_file)) == 1


def test_unknown_tool_refused(tmp_path):
    assert "no tool named" in make_tools(tmp_path).run("delete_all", {}, [])


def test_missing_value_refused(tmp_path):
    assert "missing" in make_tools(tmp_path).run("look_up_plan", {}, [])


def test_made_up_id_refused(tmp_path):
    assert "has not given" in make_tools(tmp_path).run(
        "look_up_estimate", {"estimate_id": "E102"}, customer("E101")
    )


def test_made_up_amount_refused(tmp_path):
    tools = make_tools(tmp_path)
    reply = tools.run(
        "request_down_payment_change",
        {"estimate_id": "E101", "new_down_payment": "100"},
        customer("E101 $100,000"),
    )
    assert "has not given" in reply
    assert database.waiting_requests(tools.db_file) == []


def test_calculation_does_not_save_inputs(tmp_path):
    tools = make_tools(tmp_path)
    before = database.all_estimates(tools.db_file)
    reply = tools.run(
        "calculate_example",
        {"plan_id": "P10", "home_price": "450000", "down_payment": "90000"},
        customer("P10 home $450,000 down $90,000"),
    )
    assert "$3,900.00" in reply
    assert database.all_estimates(tools.db_file) == before


@pytest.mark.parametrize("amount", ["nan", "inf", "-1", "450000"])
def test_invalid_change_refused(tmp_path, amount):
    tools = make_tools(tmp_path)
    tools.request_down_payment_change("E101", amount)
    assert database.waiting_requests(tools.db_file) == []


def test_request_status(tmp_path):
    tools = make_tools(tmp_path)
    database.add_change_request(tools.db_file, "E101", 100000)
    assert "waiting" in tools.run(
        "check_request", {"number": "1"}, customer("Request #1?")
    )
    database.approve_request(tools.db_file, 1)
    assert "approved" in tools.check_request("1")
    assert "no request" in tools.check_request("999")


def test_assistant_text_does_not_authorize_value(tmp_path):
    tools = make_tools(tmp_path)
    assert "has not given" in tools.run(
        "look_up_plan", {"plan_id": "P10"}, [{"role": "assistant", "content": "P10"}]
    )
