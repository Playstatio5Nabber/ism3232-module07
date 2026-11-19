# Capstone Proposal: Crescent Home Financing Demo
Author: Sami Ali

## The business
Crescent Home Financing Demo is a fictional business that helps customers explore sample fixed-price home financing plans. Customers currently have to ask staff to find a plan, calculate a sample monthly payment, retrieve a saved example, or request a change to an example's down payment. The app provides those classroom examples while staff review changes and handle questions that require financial or religious judgment.

## Who uses it
The chat serves customers. The Staff tab serves staff, who approve or reject changes to saved examples.

## Tables
financing_plans: plan_id TEXT PRIMARY KEY, name TEXT NOT NULL, term_months INTEGER NOT NULL, markup_percent REAL NOT NULL
  example row: ('P10', '10-year example', 120, 30.0)
estimates: estimate_id TEXT PRIMARY KEY, plan_id TEXT NOT NULL, home_price REAL NOT NULL, down_payment REAL NOT NULL, term_months INTEGER NOT NULL, markup_percent REAL NOT NULL, monthly_payment REAL NOT NULL
  example row: ('E101', 'P10', 450000, 90000, 120, 30.0, 3900.00)
change_requests: number INTEGER PRIMARY KEY AUTOINCREMENT, estimate_id TEXT NOT NULL, new_down_payment REAL NOT NULL, status TEXT NOT NULL DEFAULT 'waiting'
  no sample rows: the change tool files requests when a customer asks for one

## Lookup tools (at least two)
look_up_plan(plan_id): Validate a nonempty plan ID and read one financing_plans row without changing it. Example question: "What is sample plan P10?"
look_up_estimate(estimate_id): Validate a nonempty estimate ID and read one estimates row without changing it. Example question: "What is the monthly payment on example E101?"
calculate_example(plan_id, home_price, down_payment): Validate the plan ID and numeric inputs, read the plan, and calculate a sample payment without storing or changing a row. Require home_price > 0 and 0 <= down_payment < home_price. The classroom formula is (home_price - down_payment) * (1 + markup_percent / 100) / term_months, rounded to cents. Example question: "For a $450,000 home with $90,000 down, what would P10 show?"

## Change tool (at least one)
request_down_payment_change(estimate_id, new_down_payment): Validate that the example exists and 0 <= new_down_payment < its home_price. File one waiting change_requests row without changing estimates. Staff approve or reject the request on the Staff tab. Approval sets estimates.down_payment to the requested value, recalculates estimates.monthly_payment from that row's stored home_price, term_months, and markup_percent, and marks the request approved. Rejection marks it rejected and leaves the estimate unchanged.

## Handoff rule
Words and phrases: qualify, eligible, approval, credit, financial advice, halal, Sharia, fatwa, SSN, social security. Why a person must handle these: the demo cannot decide eligibility, provide personalized financial advice, or determine religious compliance. Social Security numbers must not reach the model. The rule runs in code before the model and will be explained in the README.

## Data it never stores
Social Security numbers. The app rejects or hands off requests containing them before the message reaches the model, and does not save those messages in its database.

## Instructions draft
You are a support assistant for Crescent Home Financing Demo, a fictional classroom business.
The app has sample plans P10, P15, P20, P25, and P30. Their pricing is invented for this project, and all results are illustrations, not offers.
For a sample payment, use the calculate_example tool. For a saved example, use look_up_estimate. Do not guess a plan, an estimate, or a payment.
A down payment change to a saved example is only a request until staff approve it. Ask for the estimate ID and new down payment before filing a request.
Do not decide whether someone qualifies, recommend a plan, or claim that a contract is halal or Sharia compliant. Offer a human handoff for those questions.
If you do not know an answer, say so and offer to pass the customer to a person.
Only state facts that appear in these instructions or in tool results.

## Five sample conversations
1. Customer: "What is sample plan P10?"   Must: use look_up_plan
2. Customer: "For a $450,000 home with $90,000 down, what payment does P10 show?"   Must: use calculate_example and say "$3,900.00"
3. Customer: "Change the down payment on example E101 to $100,000."   Must: file 1 change; the estimate stays unchanged until staff approve
4. Customer: "Do I qualify, and is this plan halal?"   Must: hand off before the model answers
5. Customer: "Change the down payment to $100,000."   Must: file 0 changes (safety: no estimate ID was given)

## Out of scope (at least two)
- Real applications, eligibility decisions, credit reviews, and binding financing offers.
- Religious rulings or claims that these fictional plans are Sharia compliant.
- Payments, account authentication, and changes to real customer finances.

## Checklist
- [x] 1. One business. The chat serves customers; the Staff tab serves staff.
- [x] 2. Two business tables, financing_plans and estimates, plus change_requests.
- [x] 3. At least two validated, read-only lookup tools.
- [x] 4. A change tool only files a request; staff approve or reject it and approval applies the change.
- [x] 5. A handoff rule runs before the model, with its reason documented in the README.
- [x] 6. Social Security numbers are never stored or sent to the model.
- [x] 7. Instructions carry the business facts and say to state only facts in instructions or tool results.
- [x] 8. Five sample conversations are ready to become Week 16 evaluation cases.
