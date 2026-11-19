import sqlite3
from datetime import date

DB_FILENAME = "expenses.db"

def get_connection():
    """Open a new connection to the SQLite database."""
    return sqlite3.connect(DB_FILENAME)

def init_db():
    """Create the expenses table if it doesn't already exist."""
    connection = get_connection()
    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT
                )
            """)
    finally:
        connection.close()

def load_expenses():
    """Reads all the expenses from the database."""
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT item, category, amount, date FROM expenses ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    expenses = []
    for item, category, amount, expense_date in rows:
        expense = {"item": item, "category": category, "amount": amount}
        if expense_date is not None:
            expense["date"] = expense_date
        expenses.append(expense)
    return expenses

# TEMPORARY: this rewrites the whole table on every save (delete everything,
# then re-insert the current list), which mirrors how the old JSON file was
# always rewritten whole. That's fine for one person using the app, but before
# adding login or hosting this for others, change add/delete to do a single
# per-row INSERT or DELETE instead, so one person's save can't wipe or race
# with another's.
def save_expenses():
    """Writes the current expenses list to the database, replacing what was there."""
    connection = get_connection()
    try:
        with connection:
            connection.execute("DELETE FROM expenses")
            for expense in expenses:
                connection.execute(
                    "INSERT INTO expenses (item, category, amount, date) VALUES (?, ?, ?, ?)",
                    (expense["item"], expense["category"], expense["amount"], expense.get("date")),
                )
    finally:
        connection.close()

init_db()
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

def create_expense(item, category, amount):
    """Build a new expense record with today's date."""
    today = date.today().isoformat()
    return {"item": item, "category": category, "amount": amount, "date": today}

def parse_amount(text):
    """Return (amount, error_message). error_message is None if the amount is valid."""
    try:
        amount = float(text)
    except ValueError:
        return None, "Please enter a number, like 4.50"
    if amount >= 0:
        return amount, None
    return None, "Please enter 0 or more."

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
        answer = input("How much did it cost (£)? ")
        if answer.lower() == "back":
            return
        amount, error = parse_amount(answer)
        if error is None:
            break
        print(error)
    expenses.append(create_expense(item, category, amount))
    save_expenses()
    print("Saved!")

def calculate_total(expenses):
    """Return the total of all expenses."""
    total = 0
    for expense in expenses:
        total = total + expense["amount"]
    return total

def calculate_category_total(expenses, category):
    """Return the total of expenses in one category."""
    total = 0
    for expense in expenses:
        if expense["category"] == category:
            total = total + expense["amount"]
    return total

def show_total():
    """Print the total of all expenses."""
    total = calculate_total(expenses)
    print(f"Total spent: £{total:.2f}")

def show_food_total():
    """Print the total of all food expenses."""
    total = calculate_category_total(expenses, "food")
    print(f"Food total: £{total:.2f}")

def calculate_category_breakdown(expenses):
    """Return a dict of {category: total} for all expenses."""
    totals = {}
    for expense in expenses:
        category = expense["category"]
        if category in totals:
            totals[category] = totals[category] + expense["amount"]
        else:
            totals[category] = expense["amount"]
    return totals

def show_report():
    """Print all different category expenses, then print the whole total."""
    if not expenses:
        print("No expenses yet.")
        return

    totals = calculate_category_breakdown(expenses)

    print("\nSpending by category:")
    for category, amount in totals.items():
        print(f"{category}: £{amount:.2f}")
    show_total()

def parse_month(text):
    """Return the month as a normalized 'YYYY-MM' string, or None if invalid."""
    parts = text.split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
        return None
    try:
        year = int(parts[0])
        month = int(parts[1])
    except ValueError:
        return None
    if 1 <= month <= 12:
        return text
    return None

def filter_by_month(expenses, month):
    """Return (matching_expenses, skipped_count) for expenses in that month."""
    matches = []
    skipped = 0
    for expense in expenses:
        if "date" not in expense:
            skipped = skipped + 1
        elif expense["date"][:7] == month:
            matches.append(expense)
    return matches, skipped

def ask_month(question):
    """Ask until the user gives a valid YYYY-MM month. Return None if they type 'back'."""
    while True:
        answer = ask_text(question)
        if answer is None:
            return None
        month = parse_month(answer)
        if month is not None:
            return month
        print("Please enter a month like 2026-11.")

def show_month_report():
    """Ask for a month and show the expenses and total for that month."""
    month = ask_month("Which month (YYYY-MM)? ")
    if month is None:
        return

    matches, skipped = filter_by_month(expenses, month)

    if not matches:
        print(f"No expenses found for {month}.")
    else:
        print(f"\nExpenses for {month}:")
        for expense in matches:
            print(f"{expense['item']}: £{expense['amount']:.2f} ({expense['date']})")
        total = calculate_total(matches)
        print(f"Total for {month}: £{total:.2f}")

    if skipped:
        print(f"({skipped} expense(s) skipped - no date saved.)")

def parse_delete_number(text, count):
    """Return (number, error_message). error_message is None if the number is valid."""
    try:
        number = int(text)
    except ValueError:
        return None, "Please enter a whole number."
    if 1 <= number <= count:
        return number, None
    return None, f"Please enter a number between 1 and {count}."

def remove_expense_at(expenses, number):
    """Remove and return the expense at the given 1-based position, then save."""
    removed = expenses.pop(number - 1)
    save_expenses()
    return removed

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
        number, error = parse_delete_number(answer, len(expenses))
        if error is None:
            break
        print(error)

    # 4. Remove it, 5. Save and confirm
    removed = remove_expense_at(expenses, number)
    print(f"Deleted: {removed['item']}")

if __name__ == "__main__":
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
#This line is for a test cmmit
