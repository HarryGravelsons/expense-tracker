import json
import os

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
    expenses.append({"item": item, "category": category, "amount": amount})
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

while True:
    print("\n1. Add expense")
    print("2. Show total")
    print("3. Show food total")
    print("4. Spending report")
    print("5. Quit")
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
        print("Goodbye!")
        break
    else:
        print("Please choose 1, 2, 3, 4 or 5.")
