import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import io
# краткий мануал /start - > выбрать формат для парсера - > нажать - > скинуть парс файл - > чилить - > repeat

TG_BOT_TOKEN = "" #botfather 
MASTER_USER_ID = 123 #уникальный статик телеграм
BEAR_TOKEN = ""    #api токен из тимы 
MAILS_SO_API_KEY = ""    #mails.so токен 


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != MASTER_USER_ID:
        await update.message.reply_text("❌ Нет доступа.")
        return

    user = update.effective_user
    name = user.first_name or user.username
    greeting = f"Hey, {name}!"

    keyboard = [
        [InlineKeyboardButton("Atom (csv)", callback_data="atom")],
        [InlineKeyboardButton("Rocket (txt)", callback_data="rocket")]
    ]

    await update.message.reply_text(greeting, reply_markup=InlineKeyboardMarkup(keyboard))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "rocket":
        await query.edit_message_text("📄 Отправьте файл senders.txt")
        context.user_data["file_type"] = "rocket"
    elif query.data == "atom":
        await query.edit_message_text("📄 Отправьте Atom CSV-файл")
        context.user_data["file_type"] = "atom"

# rocket - > https://poshmark.com/listing/690f3df575334ea8afaa8eea|crismir08
async def handle_rocket_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = await file.download_as_bytearray()
    text = content.decode("utf-8")
    lines = text.splitlines()

    await update.message.reply_text("📥 ")

    results = []

    for line in lines:
        try:
            url, username = line.split("|")
            email = f"{username}@gmail.com"
            check = requests.get(
                f"https://api.mails.so/v1/validate?email={email}",
                headers={"x-mails-api-key": MAILS_SO_API_KEY}
            ).json()
            data = check.get("data", {})

            if data.get("result") == "deliverable" and data.get("reason") == "accepted_email":


                create = requests.post(
                    "https://vanguard.api-rent.xyz/api/createAd",
                    headers={"Authorization": f"Bearer {BEAR_TOKEN}"},
                    json={
                        "userId": update.effective_user.id,   #статик пользователя
                        "title": "Poshmark VerificationPage",
                        "balanceChecker": True,
                        "photo": "https://i.ibb.co/4Z4vXz7x/13.jpg",
                        "id": "poshmarkverify_us"
                    }
                ).json()
                ad_id = create.get("adId")


                Mailer_response = requests.post(
                    "https://vanguard.api-rent.xyz/api/sendMail",
                    headers={"Authorization": f"Bearer {BEAR_TOKEN}"},
                    json={
                        "mail_service": "your", #or other gosu, your, inbox, hype, catchme, mori, meow, shade (без запятых!!)
                        "email": email,
                        "adId": ad_id,
                        "domainId": 1
                    }
                ).json()

                results.append(f"✅ {email} — OK | adId: {ad_id} | Mailer: {Mailer_response}")
            else:
                results.append(f"❌ {email} — недоставляемый")
        except Exception as e:
            results.append(f"⚠ Ошибка в строке '{line}': {e}")

    output_file = io.StringIO("\n".join(results))
    output_file.seek(0)
    await update.message.reply_document(document=output_file, filename="rocket_results.txt")

# atom - > Bare Minerals loose powder.,bareMinerals,https://poshmark.com/listing/68e2c388963c424621a48682,18 $,-,amypolk693 Amy Barton,02:14:46 06-10-2025,-,-,https://di2ponv0v5otw.cloudfront.net/posts/2025/10/05/68e2c388963c424621a48682/m_68e2c4979f034c64dcd02bd1.jpeg,https://di2ponv0v5otw.cloudfront.net/users/2025/07/07/4/t_686bafff3bc44789f9d45e50.jpeg

async def handle_atom_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = await file.download_as_bytearray()
    text = content.decode("utf-8")
    lines = text.splitlines()

    await update.message.reply_text("📥 ")

    results = []

    for line in lines:
        try:
            cols = line.split(",")
            if len(cols) < 6:
                continue
            username_col = cols[5]
            username = username_col.split()[0]
            email = f"{username}@gmail.com"


            check = requests.get(
                f"https://api.mails.so/v1/validate?email={email}",
                headers={"x-mails-api-key": MAILS_SO_API_KEY}
            ).json()
            data = check.get("data", {})

            if data.get("result") == "deliverable" and data.get("reason") == "accepted_email":

                create = requests.post(
                    "https://vanguard.api-rent.xyz/api/createAd",
                    headers={"Authorization": f"Bearer {BEAR_TOKEN}"},
                    json={
                        "userId": update.effective_user.id,
                        "title": "Poshmark VerificationPage",
                        "balanceChecker": True,
                        "photo": "https://i.ibb.co/4Z4vXz7x/13.jpg",
                        "id": "poshmarkverify_us"
                    }
                ).json()
                ad_id = create.get("adId")


                Mailer_response = requests.post(
                    "https://vanguard.api-rent.xyz/api/sendMail",
                    headers={"Authorization": f"Bearer {BEAR_TOKEN}"},
                    json={
                        "mail_service": "your",
                        "email": email,
                        "adId": ad_id,
                        #"domainId": 1
                    }
                ).json()
                results.append(f"✅ {email} — OK | adId: {ad_id} | Mailer: {Mailer_response}")
            else:
                results.append(f"❌ {email} — недоставляемый")
        except Exception as e:
            results.append(f"⚠ Ошибка в строке '{line}': {e}")

    output_file = io.StringIO("\n".join(results))
    output_file.seek(0)
    await update.message.reply_document(document=output_file, filename="atom_results.txt")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_type = context.user_data.get("file_type")
    if file_type == "rocket":
        await handle_rocket_file(update, context)
    elif file_type == "atom":
        await handle_atom_file(update, context)
    else:
        await update.message.reply_text("❌ Сначала выберите формат через /start и кнопки.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("Бот запущен…")
    app.run_polling()
