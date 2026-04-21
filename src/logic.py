import json
from models import Transaction

def load_transactions():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
            return [Transaction.from_dict(entry) for entry in data]
    except FileNotFoundError:
        return []

def save_transactions(transactions):
    with open("data.json", "w") as f:
        data = [entry.to_dict() for entry in transactions]
        json.dump(data, f, indent=2)

def get_income_sources(transactions):
    income_sources = []

    for transaction in transactions:
        if transaction.trans_type == "income":
            income_sources.append(transaction.category)
    return list(set(income_sources))

def get_balance(transaction_list: list) -> float:
    """Calculate total balance from transactions."""
    balance = 0
    
    for transaction in transaction_list:
        if transaction.trans_type == "income":
            balance += transaction.amount
        elif transaction.trans_type == "expense":
            balance -= transaction.amount
    
    return balance

def get_category_summary(cag_expense):
    """Calculates the total Expense for each category"""
    summary = {}

    for transaction in cag_expense:
        if transaction.trans_type == "expense":
            summary[transaction.category] = summary.get(transaction.category, 0) + transaction.amount
    return summary

def get_suggestions(suggestions):
    count = {}

    for transaction in suggestions:
        count[transaction.category] = count.get(transaction.category, 0) + 1
    count = sorted(count, key=lambda x: count[x], reverse=True)[:3]
    return count