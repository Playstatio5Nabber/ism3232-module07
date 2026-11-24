# Crescent Home Financing Demo — Lab 14
Author: Sami Ali

A fictional classroom assistant for invented fixed-price financing plans. Prices and markup percentages are illustrations, not offers or annual rates.

## Run
From this repository folder, activate your virtual environment and install requirements if needed:

```bash
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

The default keyword model works without Ollama and supports plan and estimate lookups. Try `What is plan P10?` and `What is estimate E101?`. Type `quit` to enter staff review.

For the local model, start Ollama, obtain the model configured in settings.py, then run `python3 main.py --ollama`. If unavailable, the app falls back to keyword lookups. Offline changes can be filed directly in Python:

```python
from database import create_tables, add_change_request

create_tables("financing.db")
add_change_request("financing.db", "E101", 100000)
```

Run main.py, type quit, and approve the request. Run it again to see the persisted down payment and recalculated payment. Tests use fresh temporary databases, leaving financing.db alone.

## Tools and staff decisions
`CrescentTools.run` rejects unknown tools, missing arguments, and protected values the customer never supplied. SQL uses parameter placeholders. The calculation tool reads a plan and does not save its inputs. Changes only insert waiting requests. Staff approval updates the estimate and request atomically; rejection leaves the estimate unchanged. A decided request cannot be approved again.

## Handoff and private information
Before recording a message or calling a model, code hands off messages containing qualify, eligible, approval, credit, financial advice, halal, Sharia, fatwa, SSN, or social security. It also rejects common nine-digit SSN formats. These questions require human financial or religious judgment. Rejected messages are not put into chat history or the database. Customers must never enter real personal or financial information; pattern checks cannot recognize every possible spelling or obfuscation. Ordinary chat history is held in memory only.

## Validation
```bash
ruff format .
ruff check .
pytest -v
```

Tests do not import ollama_model. They cover exact IDs, SQL text, repeat schema execution, numeric validation, requests and decisions, rollback, model-chosen tools, missing customer values, handoffs, and offline fallback.

Week 15's Streamlit interface is outside this Lab 14 submission. main.py provides the required terminal chat and staff review.
