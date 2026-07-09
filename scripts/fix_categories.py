with open('backend/seed_transactions.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"category": "personal"', '"category": "shopping"')

# Remove the hack from the loop
hack_code = """    if tx["category"] == "personal":
        tx["category"] = "shopping"
"""
content = content.replace(hack_code, "")

with open('backend/seed_transactions.py', 'w', encoding='utf-8') as f:
    f.write(content)
