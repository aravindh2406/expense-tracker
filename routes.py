from flask import Blueprint, render_template, request, redirect, session
from datetime import date
from database import get_db
from logic import today_total

main_routes = Blueprint("main_routes", __name__)


# ---------- REGISTER ----------
@main_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        telegram_id = request.form["telegram_id"]

        con = get_db()
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password, telegram_id) VALUES (?, ?, ?)",
                (username, password, telegram_id)
            )
            con.commit()
        except:
            con.close()
            return "User or Telegram ID already exists"

        con.close()
        return redirect("/login")

    return render_template("register.html")


# ---------- LOGIN ----------
@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = user[0]
            return redirect("/")

        return "Invalid login"

    return render_template("login.html")


# ---------- LOGOUT ----------
@main_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- DASHBOARD ----------
@main_routes.route("/", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user_id = session["user"]
    today = str(date.today())

    con = get_db()
    cur = con.cursor()

    if request.method == "POST":
        amount = int(request.form["amount"])
        note = request.form["note"]

        cur.execute(
            "INSERT INTO expenses (user_id, day, amount, note) VALUES (?, ?, ?, ?)",
            (user_id, today, amount, note)
        )
        con.commit()

    spent = today_total(user_id)

    cur.execute(
        "SELECT daily_limit, savings FROM users WHERE id=?",
        (user_id,)
    )
    daily_limit, savings = cur.fetchone()

    balance = daily_limit - spent
    alert = "⚠️ Only ₹100 left today!" if balance <= 100 else None

    cur.execute(
        "SELECT amount, note FROM expenses WHERE user_id=? AND day=?",
        (user_id, today)
    )
    expenses = cur.fetchall()

    con.close()

    return render_template(
        "dashboard.html",
        spent=spent,
        balance=balance,
        savings=savings,
        expenses=expenses,
        alert=alert
    )


# ---------- WEEKLY ----------
@main_routes.route("/weekly")
def weekly():
    if "user" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT day, SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
        """,
        (session["user"],)
    )

    data = cur.fetchall()
    con.close()

    return render_template("weekly.html", data=data)


# ---------- MONTHLY ----------
@main_routes.route("/monthly")
def monthly():
    if "user" not in session:
        return redirect("/login")

    con = get_db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT substr(day,1,7), SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY substr(day,1,7)
        """,
        (session["user"],)
    )

    data = cur.fetchall()
    con.close()

    return render_template("monthly.html", data=data)


# ---------- TELEGRAM WEBHOOK ----------
@main_routes.route("/telegram", methods=["POST"])
def telegram():
    data = request.json

    if "message" not in data:
        return "ok"

    message = data["message"]
    text = message.get("text", "")
    chat_id = str(message["chat"]["id"])

    parts = text.lower().split()

    if len(parts) < 2 or parts[0] != "expense":
        return "ok"

    try:
        amount = int(parts[1])
        note = " ".join(parts[2:]) if len(parts) > 2 else "Telegram"
    except:
        return "ok"

    con = get_db()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM users WHERE telegram_id=?",
        (chat_id,)
    )
    user = cur.fetchone()

    if user:
        cur.execute(
            "INSERT INTO expenses (user_id, day, amount, note) VALUES (?, ?, ?, ?)",
            (user[0], str(date.today()), amount, note)
        )
        con.commit()

    con.close()
    return "ok"
