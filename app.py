from flask import Flask, render_template, request, redirect, url_for, flash

import tracker

app = Flask(__name__)
app.secret_key = "dev"  # only needed so flash() messages work; this app has no logins


@app.route("/")
def index():
    expenses = tracker.load_expenses()
    total = tracker.calculate_total(expenses)
    breakdown = tracker.calculate_category_breakdown(expenses)
    return render_template(
        "index.html", expenses=expenses, total=total, breakdown=breakdown
    )


@app.route("/add", methods=["POST"])
def add():
    item = request.form.get("item", "").strip()
    category = request.form.get("category", "").strip().lower()
    amount_text = request.form.get("amount", "")

    if not item:
        flash("Please enter what you bought.")
        return redirect(url_for("index"))
    if not category:
        flash("Please enter a category.")
        return redirect(url_for("index"))

    amount, error = tracker.parse_amount(amount_text)
    if error:
        flash(error)
        return redirect(url_for("index"))

    expenses = tracker.load_expenses()
    expenses.append(tracker.create_expense(item, category, amount))
    tracker.expenses = expenses
    tracker.save_expenses()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
