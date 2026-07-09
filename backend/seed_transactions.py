import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
supabase = create_client(url, key)

import sys

transactions = [
    # MONTH 1
    {"amount": 850, "type": "income", "category": "salary", "description": "Monthly Salary", "created_at": "2026-01-01T09:00:00+03:00"},
    {"amount": 45, "type": "expense", "category": "food", "description": "Carrefour grocery run", "created_at": "2026-01-03T10:00:00+03:00"},
    {"amount": 12, "type": "expense", "category": "food", "description": "Shawarma Al-Quds restaurant", "created_at": "2026-01-07T13:30:00+03:00"},
    {"amount": 38, "type": "expense", "category": "food", "description": "Safeway weekly groceries", "created_at": "2026-01-11T16:00:00+03:00"},
    {"amount": 8, "type": "expense", "category": "food", "description": "Coffee and breakfast", "created_at": "2026-01-14T08:30:00+03:00"},
    {"amount": 42, "type": "expense", "category": "food", "description": "Carrefour monthly stock", "created_at": "2026-01-18T19:00:00+03:00"},
    {"amount": 15, "type": "expense", "category": "food", "description": "Family lunch", "created_at": "2026-01-22T14:00:00+03:00"},
    {"amount": 35, "type": "expense", "category": "food", "description": "Safeway groceries", "created_at": "2026-01-27T17:45:00+03:00"},
    {"amount": 55, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-01-04T07:15:00+03:00"},
    {"amount": 48, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-01-14T11:00:00+03:00"},
    {"amount": 40, "type": "expense", "category": "transport", "description": "Car wash and fuel top-up", "created_at": "2026-01-24T15:30:00+03:00"},
    {"amount": 22, "type": "expense", "category": "transport", "description": "Highway toll and parking fees", "created_at": "2026-01-28T18:00:00+03:00"},
    {"amount": 35, "type": "expense", "category": "utilities", "description": "Electricity bill", "created_at": "2026-01-05T09:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "utilities", "description": "Mobile phone plan", "created_at": "2026-01-05T09:10:00+03:00"},
    {"amount": 32, "type": "expense", "category": "utilities", "description": "Internet subscription", "created_at": "2026-01-05T09:15:00+03:00"},
    {"amount": 25, "type": "expense", "category": "entertainment", "description": "Netflix and Spotify subscriptions", "created_at": "2026-01-01T20:00:00+03:00"},
    {"amount": 20, "type": "expense", "category": "entertainment", "description": "Cinema tickets with friends", "created_at": "2026-01-16T19:30:00+03:00"},
    {"amount": 30, "type": "expense", "category": "entertainment", "description": "PlayStation game purchase", "created_at": "2026-01-21T21:00:00+03:00"},
    {"amount": 45, "type": "expense", "category": "shopping", "description": "Clothing purchase", "created_at": "2026-01-12T18:00:00+03:00"},
    {"amount": 25, "type": "expense", "category": "shopping", "description": "Haircut and personal care", "created_at": "2026-01-19T14:00:00+03:00"},
    {"amount": 15, "type": "expense", "category": "shopping", "description": "Pharmacy", "created_at": "2026-01-25T11:00:00+03:00"},
    {"amount": 40, "type": "expense", "category": "health", "description": "Doctor visit", "created_at": "2026-01-08T10:30:00+03:00"},
    {"amount": 25, "type": "expense", "category": "health", "description": "Pharmacy and supplements", "created_at": "2026-01-09T11:00:00+03:00"},

    # MONTH 2
    {"amount": 850, "type": "income", "category": "salary", "description": "Monthly Salary", "created_at": "2026-02-01T09:00:00+03:00"},
    {"amount": 42, "type": "expense", "category": "food", "description": "Carrefour grocery run", "created_at": "2026-02-02T10:00:00+03:00"},
    {"amount": 18, "type": "expense", "category": "food", "description": "Restaurant dinner with family", "created_at": "2026-02-06T19:00:00+03:00"},
    {"amount": 38, "type": "expense", "category": "food", "description": "Safeway weekly groceries", "created_at": "2026-02-10T15:00:00+03:00"},
    {"amount": 14, "type": "expense", "category": "food", "description": "Lunch at work area restaurant", "created_at": "2026-02-13T13:00:00+03:00"},
    {"amount": 45, "type": "expense", "category": "food", "description": "Carrefour monthly stock", "created_at": "2026-02-16T18:00:00+03:00"},
    {"amount": 22, "type": "expense", "category": "food", "description": "Valentines dinner", "created_at": "2026-02-14T20:00:00+03:00"},
    {"amount": 36, "type": "expense", "category": "food", "description": "Safeway groceries", "created_at": "2026-02-24T17:00:00+03:00"},
    {"amount": 58, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-02-03T08:00:00+03:00"},
    {"amount": 52, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-02-15T09:30:00+03:00"},
    {"amount": 38, "type": "expense", "category": "transport", "description": "Car maintenance oil change", "created_at": "2026-02-20T14:00:00+03:00"},
    {"amount": 22, "type": "expense", "category": "transport", "description": "Parking and tolls", "created_at": "2026-02-26T17:30:00+03:00"},
    {"amount": 33, "type": "expense", "category": "utilities", "description": "Electricity bill", "created_at": "2026-02-05T09:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "utilities", "description": "Mobile phone plan", "created_at": "2026-02-05T09:10:00+03:00"},
    {"amount": 31, "type": "expense", "category": "utilities", "description": "Internet subscription", "created_at": "2026-02-05T09:15:00+03:00"},
    {"amount": 25, "type": "expense", "category": "entertainment", "description": "Netflix and Spotify subscriptions", "created_at": "2026-02-01T20:00:00+03:00"},
    {"amount": 35, "type": "expense", "category": "entertainment", "description": "Evening out with friends", "created_at": "2026-02-08T21:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "entertainment", "description": "Online gaming purchase", "created_at": "2026-02-22T22:00:00+03:00"},
    {"amount": 30, "type": "expense", "category": "shopping", "description": "Clothing purchase", "created_at": "2026-02-17T16:00:00+03:00"},
    {"amount": 25, "type": "expense", "category": "shopping", "description": "Haircut and personal care", "created_at": "2026-02-25T14:30:00+03:00"},
    {"amount": 50, "type": "expense", "category": "health", "description": "Dental checkup", "created_at": "2026-02-11T10:00:00+03:00"},
    {"amount": 25, "type": "expense", "category": "health", "description": "Pharmacy", "created_at": "2026-02-12T11:00:00+03:00"},

    # MONTH 3
    {"amount": 850, "type": "income", "category": "salary", "description": "Monthly Salary", "created_at": "2026-03-01T09:00:00+03:00"},
    {"amount": 48, "type": "expense", "category": "food", "description": "Carrefour grocery run", "created_at": "2026-03-01T11:00:00+03:00"},
    {"amount": 22, "type": "expense", "category": "food", "description": "Restaurant lunch with colleagues", "created_at": "2026-03-05T13:30:00+03:00"},
    {"amount": 40, "type": "expense", "category": "food", "description": "Safeway weekly groceries", "created_at": "2026-03-09T18:00:00+03:00"},
    {"amount": 18, "type": "expense", "category": "food", "description": "Fast food and coffee", "created_at": "2026-03-12T14:00:00+03:00"},
    {"amount": 46, "type": "expense", "category": "food", "description": "Carrefour monthly stock", "created_at": "2026-03-15T19:00:00+03:00"},
    {"amount": 25, "type": "expense", "category": "food", "description": "Family dinner at restaurant", "created_at": "2026-03-20T20:30:00+03:00"},
    {"amount": 36, "type": "expense", "category": "food", "description": "Safeway groceries", "created_at": "2026-03-27T16:45:00+03:00"},
    {"amount": 60, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-03-04T07:30:00+03:00"},
    {"amount": 55, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-03-18T10:00:00+03:00"},
    {"amount": 35, "type": "expense", "category": "transport", "description": "Car service check", "created_at": "2026-03-25T14:00:00+03:00"},
    {"amount": 18, "type": "expense", "category": "transport", "description": "Parking fees", "created_at": "2026-03-30T17:00:00+03:00"},
    {"amount": 36, "type": "expense", "category": "utilities", "description": "Electricity bill", "created_at": "2026-03-05T09:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "utilities", "description": "Mobile phone plan", "created_at": "2026-03-05T09:10:00+03:00"},
    {"amount": 30, "type": "expense", "category": "utilities", "description": "Internet subscription", "created_at": "2026-03-05T09:15:00+03:00"},
    {"amount": 25, "type": "expense", "category": "entertainment", "description": "Netflix and Spotify subscriptions", "created_at": "2026-03-01T20:00:00+03:00"},
    {"amount": 40, "type": "expense", "category": "entertainment", "description": "Night out with friends", "created_at": "2026-03-14T21:30:00+03:00"},
    {"amount": 22, "type": "expense", "category": "entertainment", "description": "Cinema tickets", "created_at": "2026-03-19T19:00:00+03:00"},
    {"amount": 18, "type": "expense", "category": "entertainment", "description": "Online purchase gaming credits", "created_at": "2026-03-28T22:30:00+03:00"},
    {"amount": 25, "type": "expense", "category": "shopping", "description": "Haircut and grooming", "created_at": "2026-03-08T15:00:00+03:00"},
    {"amount": 23, "type": "expense", "category": "shopping", "description": "Pharmacy", "created_at": "2026-03-22T11:30:00+03:00"},
    {"amount": 60, "type": "expense", "category": "health", "description": "Physiotherapy session", "created_at": "2026-03-16T10:00:00+03:00"},

    # MONTH 4
    {"amount": 850, "type": "income", "category": "salary", "description": "Monthly Salary", "created_at": "2026-04-01T09:00:00+03:00"},
    {"amount": 50, "type": "expense", "category": "food", "description": "Carrefour grocery run", "created_at": "2026-04-01T10:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "food", "description": "Restaurant stress eating after car repair", "created_at": "2026-04-06T20:00:00+03:00"},
    {"amount": 42, "type": "expense", "category": "food", "description": "Safeway weekly groceries", "created_at": "2026-04-10T16:00:00+03:00"},
    {"amount": 20, "type": "expense", "category": "food", "description": "Takeaway and delivery", "created_at": "2026-04-13T21:00:00+03:00"},
    {"amount": 48, "type": "expense", "category": "food", "description": "Carrefour monthly stock", "created_at": "2026-04-17T18:00:00+03:00"},
    {"amount": 30, "type": "expense", "category": "food", "description": "Family iftar dinner", "created_at": "2026-04-21T19:30:00+03:00"},
    {"amount": 37, "type": "expense", "category": "food", "description": "Safeway groceries", "created_at": "2026-04-27T17:00:00+03:00"},
    {"amount": 62, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-04-04T08:00:00+03:00"},
    {"amount": 58, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-04-18T09:00:00+03:00"},
    {"amount": 35, "type": "expense", "category": "transport", "description": "Regular parking and tolls", "created_at": "2026-04-25T17:00:00+03:00"},
    {"amount": 20, "type": "expense", "category": "transport", "description": "Car wash", "created_at": "2026-04-29T15:00:00+03:00"},
    {"amount": 190, "type": "expense", "category": "transport", "description": "Emergency car repair transmission issue", "created_at": "2026-04-08T11:00:00+03:00"},
    {"amount": 100, "type": "expense", "category": "transport", "description": "Replacement parts and labor", "created_at": "2026-04-09T14:00:00+03:00"},
    {"amount": 37, "type": "expense", "category": "utilities", "description": "Electricity bill higher due to AC", "created_at": "2026-04-05T09:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "utilities", "description": "Mobile phone plan", "created_at": "2026-04-05T09:10:00+03:00"},
    {"amount": 30, "type": "expense", "category": "utilities", "description": "Internet subscription", "created_at": "2026-04-05T09:15:00+03:00"},
    {"amount": 25, "type": "expense", "category": "entertainment", "description": "Netflix and Spotify subscriptions", "created_at": "2026-04-01T20:00:00+03:00"},
    {"amount": 40, "type": "expense", "category": "entertainment", "description": "Eid celebration outing", "created_at": "2026-04-10T21:00:00+03:00"},
    {"amount": 25, "type": "expense", "category": "shopping", "description": "Haircut and grooming", "created_at": "2026-04-15T15:30:00+03:00"},
    {"amount": 15, "type": "expense", "category": "shopping", "description": "Pharmacy", "created_at": "2026-04-20T11:00:00+03:00"},

    # MONTH 5
    {"amount": 850, "type": "income", "category": "salary", "description": "Monthly Salary", "created_at": "2026-05-01T09:00:00+03:00"},
    {"amount": 52, "type": "expense", "category": "food", "description": "Carrefour grocery run", "created_at": "2026-05-02T10:30:00+03:00"},
    {"amount": 24, "type": "expense", "category": "food", "description": "Restaurant with family", "created_at": "2026-05-06T19:30:00+03:00"},
    {"amount": 44, "type": "expense", "category": "food", "description": "Safeway weekly groceries", "created_at": "2026-05-10T16:30:00+03:00"},
    {"amount": 22, "type": "expense", "category": "food", "description": "Lunch near work", "created_at": "2026-05-14T13:30:00+03:00"},
    {"amount": 50, "type": "expense", "category": "food", "description": "Carrefour monthly stock", "created_at": "2026-05-18T18:30:00+03:00"},
    {"amount": 32, "type": "expense", "category": "food", "description": "Dinner with friends", "created_at": "2026-05-23T20:30:00+03:00"},
    {"amount": 38, "type": "expense", "category": "food", "description": "Safeway groceries", "created_at": "2026-05-29T17:30:00+03:00"},
    {"amount": 62, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-05-05T07:45:00+03:00"},
    {"amount": 58, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-05-19T09:15:00+03:00"},
    {"amount": 32, "type": "expense", "category": "transport", "description": "Car wash and minor service", "created_at": "2026-05-26T15:00:00+03:00"},
    {"amount": 20, "type": "expense", "category": "transport", "description": "Parking and tolls", "created_at": "2026-05-30T17:30:00+03:00"},
    {"amount": 38, "type": "expense", "category": "utilities", "description": "Electricity bill", "created_at": "2026-05-05T09:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "utilities", "description": "Mobile phone plan", "created_at": "2026-05-05T09:10:00+03:00"},
    {"amount": 30, "type": "expense", "category": "utilities", "description": "Internet subscription", "created_at": "2026-05-05T09:15:00+03:00"},
    {"amount": 25, "type": "expense", "category": "entertainment", "description": "Netflix and Spotify subscriptions", "created_at": "2026-05-01T20:00:00+03:00"},
    {"amount": 45, "type": "expense", "category": "entertainment", "description": "Concert tickets", "created_at": "2026-05-16T19:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "entertainment", "description": "Night out", "created_at": "2026-05-24T22:00:00+03:00"},
    {"amount": 20, "type": "expense", "category": "entertainment", "description": "Online subscription service", "created_at": "2026-05-30T21:00:00+03:00"},
    {"amount": 30, "type": "expense", "category": "shopping", "description": "New clothing", "created_at": "2026-05-12T16:00:00+03:00"},
    {"amount": 22, "type": "expense", "category": "shopping", "description": "Haircut and pharmacy", "created_at": "2026-05-27T14:00:00+03:00"},
    {"amount": 30, "type": "expense", "category": "health", "description": "Pharmacy and vitamins", "created_at": "2026-05-20T10:30:00+03:00"},

    # MONTH 6
    {"amount": 850, "type": "income", "category": "salary", "description": "Monthly Salary", "created_at": "2026-06-01T09:00:00+03:00"},
    {"amount": 55, "type": "expense", "category": "food", "description": "Carrefour grocery run", "created_at": "2026-06-01T11:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "food", "description": "Restaurant dinner", "created_at": "2026-06-05T20:00:00+03:00"},
    {"amount": 46, "type": "expense", "category": "food", "description": "Safeway weekly groceries", "created_at": "2026-06-09T17:00:00+03:00"},
    {"amount": 25, "type": "expense", "category": "food", "description": "Lunch and coffee", "created_at": "2026-06-12T13:00:00+03:00"},
    {"amount": 52, "type": "expense", "category": "food", "description": "Carrefour monthly stock", "created_at": "2026-06-16T18:00:00+03:00"},
    {"amount": 35, "type": "expense", "category": "food", "description": "Family dinner out", "created_at": "2026-06-21T19:30:00+03:00"},
    {"amount": 37, "type": "expense", "category": "food", "description": "Safeway groceries", "created_at": "2026-06-27T16:30:00+03:00"},
    {"amount": 62, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-06-03T08:15:00+03:00"},
    {"amount": 58, "type": "expense", "category": "transport", "description": "Fuel for Careem shifts", "created_at": "2026-06-17T09:30:00+03:00"},
    {"amount": 30, "type": "expense", "category": "transport", "description": "Car wash and service", "created_at": "2026-06-24T15:30:00+03:00"},
    {"amount": 20, "type": "expense", "category": "transport", "description": "Parking and tolls", "created_at": "2026-06-29T17:45:00+03:00"},
    {"amount": 40, "type": "expense", "category": "utilities", "description": "Electricity bill summer increase", "created_at": "2026-06-05T09:00:00+03:00"},
    {"amount": 28, "type": "expense", "category": "utilities", "description": "Mobile phone plan", "created_at": "2026-06-05T09:10:00+03:00"},
    {"amount": 30, "type": "expense", "category": "utilities", "description": "Internet subscription", "created_at": "2026-06-05T09:15:00+03:00"},
    {"amount": 25, "type": "expense", "category": "entertainment", "description": "Netflix and Spotify subscriptions", "created_at": "2026-06-01T20:00:00+03:00"},
    {"amount": 50, "type": "expense", "category": "entertainment", "description": "Weekend trip with friends", "created_at": "2026-06-13T12:00:00+03:00"},
    {"amount": 33, "type": "expense", "category": "entertainment", "description": "Dinner and shisha evening", "created_at": "2026-06-20T21:30:00+03:00"},
    {"amount": 20, "type": "expense", "category": "entertainment", "description": "Online gaming purchase", "created_at": "2026-06-28T22:30:00+03:00"},
    {"amount": 45, "type": "expense", "category": "shopping", "description": "Summer clothing purchase", "created_at": "2026-06-08T16:30:00+03:00"},
    {"amount": 29, "type": "expense", "category": "shopping", "description": "Haircut and personal care", "created_at": "2026-06-25T14:30:00+03:00"},
]

if len(sys.argv) > 1 and sys.argv[1] == "clear":
    res = supabase.table("transactions").delete().eq("user_email", "anas@tamweel.ai").execute()
    print(f"Cleared transactions for anas@tamweel.ai")
    sys.exit(0)

for tx in transactions:
    tx["user_email"] = "anas@tamweel.ai"
    res = supabase.table("transactions").insert(tx).execute()
    if res.data:
        print(f"Inserted: {tx['description']} - {tx['amount']}")
    else:
        print(f"Failed to insert: {tx['description']}")

print(f"Finished seeding {len(transactions)} transactions.")
