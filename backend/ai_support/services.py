from django.conf import settings
from openai import OpenAI
import requests


def get_openai_client():

    if not settings.OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not configured.")

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )

    return client


def get_ultron_response(customer_message):

    client = get_openai_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ULTRON, an AI-powered customer support "
                    "assistant. Help customers with their queries "
                    "in a clear, polite, and professional manner."
                )
            },
            {
                "role": "user",
                "content": customer_message
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content



def get_ultron_ollama_response(customer_message):

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:1b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are ULTRON, an AI-powered customer "
                        "support assistant. Help customers with "
                        "their queries in a clear, polite, "
                        "and professional manner."
                    )
                },
                {
                    "role": "user",
                    "content": customer_message
                }
            ],
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["message"]["content"]




def classify_customer_query(customer_message):

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:1b",
            "messages": [
                {
                    "role": "system",
                    "content": """
You are a customer support ticket classifier.

Your task is to identify the MAIN issue in the customer's message.

Choose exactly ONE category:

TECH:
Software bugs, application crashes, technical errors,
website problems, loading problems, server issues.

BILL:
Payments, invoices, subscriptions, refunds,
duplicate charges, billing disputes.

ACC:
Login problems, password resets, account access,
registration, profile updates, account settings.

GEN:
General questions, product information, service enquiries,
feedback, and anything that does not fit the other categories.

Examples:

"My application crashes when I open it."
Answer: TECH

"I was charged twice for my subscription."
Answer: BILL

"I cannot reset my password."
Answer: ACC

"What services does your company provide?"
Answer: GEN

Important rules:
- Read the customer's actual issue carefully.
- Do not classify every query as TECH.
- Select the category that best matches the main issue.
- Return ONLY one of these exact codes:
TECH
BILL
ACC
GEN
- Do not include explanations or additional text.
"""
                },
                {
                    "role": "user",
                    "content": customer_message
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0
            }
        },
        timeout=120
    )

    response.raise_for_status()

    category = response.json()["message"]["content"].strip().upper()

    allowed_categories = ["TECH", "BILL", "ACC", "GEN"]

    if category not in allowed_categories:
        return "GEN"

    return category


