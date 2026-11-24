# main.py
# Author: Sami Ali
import argparse

from agent import SupportChatbot
from database import (
    all_estimates,
    approve_request,
    create_tables,
    reject_request,
    waiting_requests,
)
from keyword_model import KeywordModel
from settings import DB_FILE, INSTRUCTIONS, MODEL_NAME
from tools import CrescentTools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ollama", action="store_true", help="Use Ollama with offline fallback"
    )
    args = parser.parse_args()
    model = KeywordModel()
    if args.ollama:
        from fallback_model import FallbackModel
        from ollama_model import OllamaModel

        model = FallbackModel(OllamaModel(MODEL_NAME), model)
    create_tables(DB_FILE)
    bot = SupportChatbot("Crescent", INSTRUCTIONS, CrescentTools(DB_FILE), model)
    print("Fictional classroom examples only. Type quit to stop.")
    while True:
        message = input("You: ")
        if message == "quit":
            break
        print(f"{bot.name}: {bot.respond(message)}")
    print(f"Messages in this conversation: {len(bot.history)}")
    print("Staff review")
    for request in waiting_requests(DB_FILE):
        number = request["number"]
        print(
            f"Request {number}: {request['estimate_id']} to ${request['new_down_payment']:,.2f} down"
        )
        answer = input("Approve? yes or no: ")
        if answer == "yes":
            print(approve_request(DB_FILE, number))
        elif answer == "no":
            print(reject_request(DB_FILE, number))
        else:
            print(f"Request {number} is still waiting.")
    for estimate in all_estimates(DB_FILE):
        print(
            estimate["estimate_id"],
            estimate["down_payment"],
            estimate["monthly_payment"],
        )


if __name__ == "__main__":
    main()
