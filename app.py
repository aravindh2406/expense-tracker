from flask import Flask, render_template, request, redirect, session
from logic import *

app = Flask(__name__)
app.secret_key = "secret"

# Initialize database
init_db()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user_id = int(request.form["user_id"])
            session["user_id"] = user_id
            return redirect("/dashboard")
        except:
            return "Invalid User ID"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    # Fetch all data
    balance = get_balance(user_id)
    expenses = get_all_expenses(user_id)

    daily_limit, weekly_limit = get_limits(user_id)
    alert = check_alert(user_id)

    salary = get_salary(user_id)
    daily_spent = get_daily_spent(user_id)
    weekly_spent = get_weekly_spent(user_id)

    return render_template(
        "dashboard.html",
        balance=balance,
        expenses=expenses,
        salary=salary,
        daily_spent=daily_spent,
        weekly_spent=weekly_spent,
        daily_limit=daily_limit,
        weekly_limit=weekly_limit,
        alert=alert
    )


# ---------------- SET SALARY ----------------
@app.route("/set_salary", methods=["POST"])
def set_salary_web():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    try:
        amount = int(request.form["salary"])
        set_salary(user_id, amount)
    except:
        pass

    return redirect("/dashboard")


# ---------------- SET LIMITS ----------------
@app.route("/set_limits", methods=["POST"])
def set_limits_web():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    try:
        daily = int(request.form["daily"])
        weekly = int(request.form["weekly"])
        set_limits(user_id, daily, weekly)
    except:
        pass

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)