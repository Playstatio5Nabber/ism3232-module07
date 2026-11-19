-- Fictional home financing plans for classroom estimates.
-- Markup percentages are total examples for the full term, not annual rates.
CREATE TABLE IF NOT EXISTS financing_plans (
    plan_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    term_months INTEGER NOT NULL,
    markup_percent REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS estimates (
    estimate_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    home_price REAL NOT NULL,
    down_payment REAL NOT NULL,
    term_months INTEGER NOT NULL,
    markup_percent REAL NOT NULL,
    monthly_payment REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS change_requests (
    number INTEGER PRIMARY KEY AUTOINCREMENT,
    estimate_id TEXT NOT NULL,
    new_down_payment REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'waiting'
);

-- Classroom examples only; these are not real financing offers.
INSERT OR IGNORE INTO financing_plans
    (plan_id, name, term_months, markup_percent)
VALUES
    ('P10', '10-year example', 120, 30.0),
    ('P15', '15-year example', 180, 45.0),
    ('P20', '20-year example', 240, 60.0),
    ('P25', '25-year example', 300, 75.0),
    ('P30', '30-year example', 360, 90.0);

-- Fictional saved estimates for lookup practice.
-- Payment = (home_price - down_payment) * (1 + markup_percent / 100) / term_months.
INSERT OR IGNORE INTO estimates
    (estimate_id, plan_id, home_price, down_payment,
     term_months, markup_percent, monthly_payment)
VALUES
    ('E101', 'P10', 450000, 90000, 120, 30.0, 3900.00),
    ('E102', 'P20', 300000, 60000, 240, 60.0, 1600.00),
    ('E103', 'P15', 350000, 70000, 180, 45.0, 2255.56),
    ('E104', 'P25', 500000, 100000, 300, 75.0, 2333.33),
    ('E105', 'P30', 250000, 50000, 360, 90.0, 1055.56);
