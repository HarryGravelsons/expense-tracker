import json
import os

import tracker

JSON_FILENAME = "expenses.json"

def load_json_expenses():
    """Reads expenses directly from the old JSON file (not through tracker)."""
    if not os.path.exists(JSON_FILENAME):
        return []
    with open(JSON_FILENAME, "r") as file:
        return json.load(file)

def main():
    """One-off migration: copy expenses.json into the SQLite database."""
    tracker.init_db()

    connection = tracker.get_connection()
    try:
        existing_count = connection.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    finally:
        connection.close()

    if existing_count > 0:
        print(f"The database already has {existing_count} expense(s). Migration skipped to avoid duplicates.")
        return

    old_expenses = load_json_expenses()
    if not old_expenses:
        print("No expenses.json data found to migrate.")
        return

    no_date_count = 0
    connection = tracker.get_connection()
    try:
        with connection:
            for expense in old_expenses:
                expense_date = expense.get("date")
                if expense_date is None:
                    no_date_count = no_date_count + 1
                connection.execute(
                    "INSERT INTO expenses (item, category, amount, date) VALUES (?, ?, ?, ?)",
                    (expense["item"], expense["category"], expense["amount"], expense_date),
                )
    finally:
        connection.close()

    print(f"Migrated {len(old_expenses)} expense(s) ({no_date_count} with no date).")
    print("expenses.json was not changed or deleted - it's still there untouched, in case you want to double check anything.")

if __name__ == "__main__":
    main()
