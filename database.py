# database.py
# Author: Sami Ali
import math
import sqlite3


def query_all(db_file, sql, values=()):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, values).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def query_one(db_file, sql, values=()):
    rows = query_all(db_file, sql, values)
    return rows[0] if rows else None


def change(db_file, sql, values=()):
    conn = sqlite3.connect(db_file)
    cursor = conn.execute(sql, values)
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def create_tables(db_file):
    with open("schema.sql") as f:
        script = f.read()
    conn = sqlite3.connect(db_file)
    conn.executescript(script)
    conn.commit()
    conn.close()


def find_plan(db_file, plan_id):
    return query_one(
        db_file, "SELECT * FROM financing_plans WHERE plan_id = ?", (plan_id,)
    )


def find_estimate(db_file, estimate_id):
    return query_one(
        db_file, "SELECT * FROM estimates WHERE estimate_id = ?", (estimate_id,)
    )


def payment(home_price, down_payment, term_months, markup_percent):
    return round(
        (home_price - down_payment) * (1 + markup_percent / 100) / term_months, 2
    )


def valid_down_payment(estimate, value):
    return math.isfinite(value) and 0 <= value < estimate["home_price"]


def add_change_request(db_file, estimate_id, new_down_payment):
    estimate = find_estimate(db_file, estimate_id)
    if estimate is None or not valid_down_payment(estimate, new_down_payment):
        raise ValueError("Invalid estimate or down payment.")
    return change(
        db_file,
        "INSERT INTO change_requests (estimate_id, new_down_payment) VALUES (?, ?)",
        (estimate_id, new_down_payment),
    )


def find_request(db_file, number):
    return query_one(
        db_file, "SELECT * FROM change_requests WHERE number = ?", (number,)
    )


def waiting_requests(db_file):
    return query_all(
        db_file,
        "SELECT * FROM change_requests WHERE status = 'waiting' ORDER BY number",
    )


def approve_request(db_file, number):
    # Keep the record change and request decision in one transaction.
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("BEGIN IMMEDIATE")
        request = conn.execute(
            "SELECT * FROM change_requests WHERE number = ?", (number,)
        ).fetchone()
        if request is None:
            return f"There is no request {number}."
        if request["status"] != "waiting":
            return f"Request {number} is already {request['status']}."
        estimate = conn.execute(
            "SELECT * FROM estimates WHERE estimate_id = ?", (request["estimate_id"],)
        ).fetchone()
        if estimate is None or not valid_down_payment(
            estimate, request["new_down_payment"]
        ):
            return f"Request {number} has an invalid estimate or down payment."
        monthly = payment(
            estimate["home_price"],
            request["new_down_payment"],
            estimate["term_months"],
            estimate["markup_percent"],
        )
        conn.execute(
            "UPDATE estimates SET down_payment = ?, monthly_payment = ? WHERE estimate_id = ?",
            (request["new_down_payment"], monthly, request["estimate_id"]),
        )
        conn.execute(
            "UPDATE change_requests SET status = 'approved' WHERE number = ?", (number,)
        )
        conn.commit()
        return f"Request {number} approved."
    finally:
        conn.close()


def reject_request(db_file, number):
    request = find_request(db_file, number)
    if request is None:
        return f"There is no request {number}."
    if request["status"] != "waiting":
        return f"Request {number} is already {request['status']}."
    change(
        db_file,
        "UPDATE change_requests SET status = 'rejected' WHERE number = ? AND status = 'waiting'",
        (number,),
    )
    return f"Request {number} rejected."


def all_estimates(db_file):
    return query_all(db_file, "SELECT * FROM estimates ORDER BY estimate_id")
