import sqlite3

import pytest

import database


def make_db(tmp_path):
    db = tmp_path / "test.db"
    database.create_tables(db)
    return db


def test_create_tables_twice_adds_no_duplicate_rows(tmp_path):
    db = make_db(tmp_path)
    database.create_tables(db)
    assert len(database.all_estimates(db)) == 5
    assert len(database.query_all(db, "SELECT * FROM financing_plans")) == 5


def test_lookup_needs_exact_id(tmp_path):
    db = make_db(tmp_path)
    assert database.find_estimate(db, "E101")["monthly_payment"] == 3900
    assert database.find_plan(db, "P10")["term_months"] == 120
    assert database.find_estimate(db, "E10") is None


def test_sql_in_id_is_just_text(tmp_path):
    db = make_db(tmp_path)
    assert database.find_estimate(db, "E101' OR '1'='1") is None
    assert database.find_plan(db, "P10' OR '1'='1") is None


def test_change_gets_number_and_waits(tmp_path):
    db = make_db(tmp_path)
    number = database.add_change_request(db, "E101", 100000)
    assert number == 1
    assert database.find_request(db, number)["status"] == "waiting"
    assert database.find_estimate(db, "E101")["down_payment"] == 90000


def test_approve_changes_record_once_and_persists(tmp_path):
    db = make_db(tmp_path)
    database.add_change_request(db, "E101", 100000)
    assert database.approve_request(db, 1) == "Request 1 approved."
    assert database.find_estimate(db, "E101")["monthly_payment"] == 3791.67
    assert database.find_estimate(db, "E101")["down_payment"] == 100000
    assert database.approve_request(db, 1) == "Request 1 is already approved."
    assert database.waiting_requests(db) == []
    database.create_tables(db)
    assert database.find_estimate(db, "E101")["down_payment"] == 100000


def test_reject_leaves_record_and_blocks_later_approval(tmp_path):
    db = make_db(tmp_path)
    database.add_change_request(db, "E101", 100000)
    assert database.reject_request(db, 1) == "Request 1 rejected."
    assert database.approve_request(db, 1) == "Request 1 is already rejected."
    assert database.find_estimate(db, "E101")["down_payment"] == 90000


@pytest.mark.parametrize("amount", [-1, 450000, float("inf"), float("nan")])
def test_invalid_down_payment_is_not_filed(tmp_path, amount):
    db = make_db(tmp_path)
    with pytest.raises(ValueError):
        database.add_change_request(db, "E101", amount)
    assert database.waiting_requests(db) == []


def test_approval_rolls_back_when_record_update_fails(tmp_path):
    db = make_db(tmp_path)
    database.add_change_request(db, "E101", 100000)
    database.change(
        db,
        "CREATE TRIGGER fail_update BEFORE UPDATE ON estimates BEGIN SELECT RAISE(ABORT, 'test failure'); END",
    )
    with pytest.raises(sqlite3.IntegrityError):
        database.approve_request(db, 1)
    assert database.find_request(db, 1)["status"] == "waiting"
    assert database.find_estimate(db, "E101")["down_payment"] == 90000
