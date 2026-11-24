# tools.py
# Author: Sami Ali
import math
import re

import database


class CrescentTools:
    """Validated database tools for fictional classroom examples."""

    def __init__(self, db_file):
        self.db_file = db_file

    def tool_list(self):
        return [
            self.look_up_plan,
            self.look_up_estimate,
            self.calculate_example,
            self.request_down_payment_change,
            self.check_request,
        ]

    def look_up_plan(self, plan_id):
        """Look up an invented financing plan.

        Args:
            plan_id: The plan ID, like P10.
        """
        for word in plan_id.upper().split():
            plan = database.find_plan(self.db_file, word.strip("?.!,#"))
            if plan is not None:
                return f"Plan {plan['plan_id']}: {plan['term_months']} months, {plan['markup_percent']:.2f}% total markup. Classroom example only."
        return "No plan with that ID was found."

    def look_up_estimate(self, estimate_id):
        """Look up one saved classroom estimate.

        Args:
            estimate_id: The estimate ID, like E101.
        """
        for word in estimate_id.upper().split():
            estimate = database.find_estimate(self.db_file, word.strip("?.!,#"))
            if estimate is not None:
                return f"Example {estimate['estimate_id']}: ${estimate['monthly_payment']:,.2f} per month, with ${estimate['down_payment']:,.2f} down. Classroom example only."
        return "No estimate with that ID was found."

    def calculate_example(self, plan_id, home_price, down_payment):
        """Calculate a fictional payment without saving the inputs.

        Args:
            plan_id: The plan ID, like P10.
            home_price: The sample home price.
            down_payment: The sample down payment.
        """
        plan = database.find_plan(self.db_file, plan_id.upper())
        if plan is None:
            return "No plan with that ID was found."
        try:
            price = self.amount(home_price)
            down = self.amount(down_payment)
        except ValueError:
            return "Enter finite numeric amounts."
        if price <= 0 or not 0 <= down < price:
            return "Home price must be positive and down payment must be between zero and less than the home price."
        monthly = database.payment(
            price, down, plan["term_months"], plan["markup_percent"]
        )
        return f"Classroom example: ${monthly:,.2f} per month. These inputs were not saved."

    def request_down_payment_change(self, estimate_id, new_down_payment):
        """File a request for staff; do not change the estimate yet.

        Args:
            estimate_id: The saved estimate ID, like E101.
            new_down_payment: The requested down payment.
        """
        try:
            number = database.add_change_request(
                self.db_file, estimate_id.upper(), self.amount(new_down_payment)
            )
        except ValueError:
            return "Enter an existing estimate ID and a finite down payment from zero to less than its home price."
        return f"Request {number} was sent to staff. The estimate has not changed yet."

    def check_request(self, number):
        """Check the staff decision for a request.

        Args:
            number: The request number, like 3.
        """
        try:
            request = database.find_request(self.db_file, int(number))
        except (ValueError, OverflowError):
            return "Enter a valid request number."
        if request is None:
            return f"There is no request {number}."
        return f"Request {number} for example {request['estimate_id']} is {request['status']}."

    def run(self, name, arguments, history):
        specs = {
            "look_up_plan": ["plan_id"],
            "look_up_estimate": ["estimate_id"],
            "calculate_example": ["plan_id", "home_price", "down_payment"],
            "request_down_payment_change": ["estimate_id", "new_down_payment"],
            "check_request": ["number"],
        }
        if name not in specs:
            return f"There is no tool named {name}."
        if not isinstance(arguments, dict):
            return "Tool arguments must be a dictionary."
        values = {}
        for key in specs[name]:
            value = self.clean(arguments, key)
            if value == "":
                return f"The {key} is missing. Ask the customer for it."
            if key in ("home_price", "down_payment", "new_down_payment"):
                said = self.customer_said_amount(history, value)
            else:
                said = self.customer_said(history, value)
            if not said:
                return f"The customer has not given that {key}. Ask them for it."
            values[key] = value
        return getattr(self, name)(**values)

    def amount(self, text):
        value = float(str(text).replace("$", "").replace(",", ""))
        if not math.isfinite(value):
            raise ValueError("Amount must be finite.")
        return value

    def customer_said_amount(self, history, text):
        try:
            wanted = self.amount(text)
        except ValueError:
            return False
        # Match a complete amount, so 100 cannot match 100000.
        for message in history:
            if message["role"] == "user":
                amounts = re.findall(
                    r"(?<![\w.])-?\$?\d[\d,]*(?:\.\d+)?(?!\w)", message["content"]
                )
                if any(self.amount(amount) == wanted for amount in amounts):
                    return True
        return False

    def clean(self, arguments, key):
        """Return one argument as text without extra spaces, or empty if missing."""
        return str(arguments.get(key, "")).strip()

    def words(self, text):
        """Return text in lower case as whole words, without ?.!,# around each word."""
        cleaned = []
        for word in text.lower().split():
            cleaned.append(word.strip("?.!,#"))
        return " " + " ".join(cleaned) + " "

    def customer_said(self, history, text):
        """Return True if the customer typed text as whole words."""
        wanted = self.words(text)
        for message in history:
            if message["role"] == "user" and wanted in self.words(message["content"]):
                return True
        return False
