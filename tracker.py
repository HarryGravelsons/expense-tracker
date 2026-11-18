import json
import os
from datetime import date

FILENAME = "expenses.json"

def load_expenses():
    """Reads all the expenses from the JSON file."""
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as file:
            return json.load(file)
    return []

def save_expenses():
    """Writes the new expenses to the JSON file."""
    with open(FILENAME, "w") as file:
        json.dump(expenses, file, indent=2)

expenses = load_expenses()

def ask_text(question):
    """Ask until the user gives a non-empty answer. Return None if they type 'back'."""
    while True:
        answer = input(question).strip()
        if answer.lower() == "back":
            return None
        if answer:
            return answer
        print("Please enter something.")

def add_expense():
    """Ask the user to input a new expense."""
    item = ask_text("What did you buy? ")
    if item is None:
        return
    category = ask_text("What category is it? ")
    if category is None:
        return
    category = category.lower()
    while True:
        try:
            answer = input("How much did it cost (£)? ")
            if answer.lower() == "back":
                return
            amount = float(answer)
            if amount >= 0:
                break
            else:
                print("Please enter 0 or more.")
        except ValueError:
            print("Please enter a number, like 4.50")
    today = date.today().isoformat()
    expenses.append({"item": item, "category": category, "amount": amount, "date": today})
    save_expenses()
    print("Saved!")

def show_total():
    """Print the total of all expenses."""
    total = 0
    for expense in expenses:
        total = total + expense["amount"]
    print(f"Total spent: £{total:.2f}")

def show_food_total():
    """Print the total of all food expenses."""
    total = 0
    for expense in expenses:
        if expense["category"] == "food":
            total = total + expense["amount"]
    print(f"Food total: £{total:.2f}")

def show_report():
    """Print all different category expenses, then print the whole total."""
    if not expenses:
        print("No expenses yet.")
        return

    totals = {}
    for expense in expenses:
        category = expense["category"]
        if category in totals:
            totals[category] = totals[category] + expense["amount"]
        else:
            totals[category] = expense["amount"]

    print("\nSpending by category:")
    for category, amount in totals.items():
        print(f"{category}: £{amount:.2f}")
    show_total()

def ask_month(question):
    """Ask until the user gives a valid YYYY-MM month. Return None if they type 'back'."""
    while True:
        answer = ask_text(question)
        if answer is None:
            return None
        parts = answer.split("-")
        if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
            print("Please enter a month like 2026-11.")
            continue
        try:
            year = int(parts[0])
            month = int(parts[1])
        except ValueError:
            print("Please enter a month like 2026-11.")
            continue
        if 1 <= month <= 12:
            return answer
        print("Please enter a month like 2026-11.")

def show_month_report():
    """Ask for a month and show the expenses and total for that month."""
    month = ask_month("Which month (YYYY-MM)? ")
    if month is None:
        return

    matches = []
    skipped = 0
    for expense in expenses:
        if "date" not in expense:
            skipped = skipped + 1
        elif expense["date"][:7] == month:
            matches.append(expense)

    if not matches:
        print(f"No expenses found for {month}.")
    else:
        print(f"\nExpenses for {month}:")
        total = 0
        for expense in matches:
            print(f"{expense['item']}: £{expense['amount']:.2f} ({expense['date']})")
            total = total + expense["amount"]
        print(f"Total for {month}: £{total:.2f}")

    if skipped:
        print(f"({skipped} expense(s) skipped - no date saved.)")

def delete_expense():
    """Let the user remove one expense by number."""
    if not expenses:
        print("No expenses to delete.")
        return

    # 1. Show the expenses with numbers
    for number, expense in enumerate(expenses, start=1):
        expense_date = expense.get("date", "unknown")
        print(f"{number}. {expense['item']}: £{expense['amount']:.2f} ({expense_date})")

    # 2 and 3. Ask which one, and check it's valid
    while True:
        answer = input("Number to delete (or 'back'): ").strip().lower()
        if answer == "back":
            return
        try:
            number = int(answer)
            if 1 <= number <= len(expenses):
                break
            else:
                print(f"Please enter a number between 1 and {len(expenses)}.")
        except ValueError:
            print("Please enter a whole number.")

    # 4. Remove it (remember: list positions start at 0!)
    removed = expenses.pop(number -1)

    # 5. Save and confirm
    save_expenses()
    print(f"Deleted: {removed['item']}")

while True:
    print("\n1. Add expense")
    print("2. Show total")
    print("3. Show food total")
    print("4. Spending report")
    print("5. Delete expense")
    print("6. Monthly report")
    print("7. Quit")
    choice = input("Choose an option: ")

    if choice == "1":
        add_expense()
    elif choice == "2":
        show_total()
    elif choice == "3":
        show_food_total()
    elif choice == "4":
        show_report()
    elif choice == "5":
        delete_expense()
    elif choice == "6":
        show_month_report()
    elif choice == "7":
        print("Goodbye!")
        break
    else:
        print("Please choose 1, 2, 3, 4, 5, 6 or 7.")
