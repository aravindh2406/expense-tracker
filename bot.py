from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from logic import *

init_db()

TOKEN = "8264392446:AAGLBjQE1KfBB3zRQ0LV-qm_j6CD9yJ0_F8"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text(
        "/salary 10000\n"
        "/limit 500 3000\n"
        "200 food\n"
        "/balance"
    )


async def set_salary_command(update, context):
    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage: /setsalary 50000"
        )
        return

    try:
        amount = int(context.args[0])

        await update.message.reply_text(
            f"Salary set to ₹{amount}"
        )

    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number."
        )


async def set_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    daily = int(context.args[0])
    weekly = int(context.args[1])

    set_limits(user_id, daily, weekly)

    await update.message.reply_text("✅ Limits set")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    bal = get_balance(user_id)
    await update.message.reply_text(f"💰 Balance: ₹{bal}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    register_user(user_id, user.username or "user")

    text = update.message.text.lower().split()

    try:
        amount = int(text[0])
        category = " ".join(text[1:])

        add_expense(user_id, amount, category)

        await update.message.reply_text("✅ Expense added")

        alert = check_alert(user_id)
        if alert:
            await update.message.reply_text(alert)

    except:
        await update.message.reply_text("Use: 200 food")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("salary", set_salary_command))
app.add_handler(CommandHandler("limit", set_limit))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling(
    drop_pending_updates=True,
    close_loop=False
)