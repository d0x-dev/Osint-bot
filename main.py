import telebot
import requests

BOT_TOKEN = "8383101634:AAEuyXuWQzTjKpurTjQRCNBIkal432VF3_k"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

API_URL = "https://e1e63696f2d5.ngrok-free.app/index.cpp?key=dark&number="

# Stylish bold labels using Unicode characters
LABELS = {
    "number": "📞 𝗡𝘂𝗺𝗯𝗲𝗿",
    "name": "👤 𝗡𝗮𝗺𝗲",
    "father": "👨‍👦 𝗙𝗮𝘁𝗵𝗲𝗿",
    "address": "🏠 𝗔𝗱𝗱𝗿𝗲𝘀𝘀",
    "circle": "📍 𝗖𝗶𝗿𝗰𝗹𝗲",
    "alt": "🔗 𝗔𝗹𝘁",
    "aadhaar": "🆔 𝗔𝗮𝗱𝗵𝗮𝗮𝗿",
}


def clean_address(address: str) -> str:
    """Clean address by replacing !! and ! with commas"""
    if not address:
        return "N/A"
    return address.replace("!!", ", ").replace("!", ", ")


def fetch_number_details(number, visited=None):
    """Fetch details + recursively fetch alt numbers"""
    if visited is None:
        visited = set()

    number = number[-10:]
    if number in visited:
        return []

    visited.add(number)

    try:
        url = f"{API_URL}{number}"
        r = requests.get(url, timeout=10)
        data = r.json().get("data", [])
    except Exception as e:
        return [{"error": str(e)}]

    results = []
    for item in data:
        results.append({
            "mobile": item.get("mobile", "N/A"),
            "name": item.get("name", "N/A"),
            "fname": item.get("fname", "N/A"),
            "address": clean_address(item.get("address", "N/A")),
            "circle": item.get("circle", "N/A"),
            "alt": item.get("alt", "N/A"),
            "aadhaar": item.get("id", "N/A"),
        })

        # Recursive alt lookup
        alt = item.get("alt", "")
        if alt and alt.isdigit():
            alt_num = alt[-10:]
            if alt_num not in visited:
                results.extend(fetch_number_details(alt_num, visited))

    return results


def format_results(results):
    """Format results in a stylish profile card format"""
    blocks = []
    for item in results:
        if "error" in item:
            blocks.append(f"❌ Error fetching: <code>{item['error']}</code>")
            continue

        text = (
            "━━━━━━━━━━━━━━━\n"
            f"{LABELS['number']}: <code>{item['mobile']}</code>\n"
            f"{LABELS['name']}: <code>{item['name']}</code>\n"
            f"{LABELS['father']}: <code>{item['fname']}</code>\n"
            f"{LABELS['address']}: <code>{item['address']}</code>\n"
            f"{LABELS['circle']}: <code>{item['circle']}</code>\n"
            f"{LABELS['alt']}: <code>{item['alt']}</code>\n"
            f"{LABELS['aadhaar']}: <code>{item['aadhaar']}</code>\n"
            "━━━━━━━━━━━━━━━"
        )
        blocks.append(text)

    return "\n\n".join(blocks)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    dev_btn = telebot.types.InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/YOUR_USERNAME")
    chan_btn = telebot.types.InlineKeyboardButton("📢 Channel", url="https://t.me/stormxvup")
    markup.row(dev_btn, chan_btn)

    text = (
        "<b>🤖 Phone Info Bot</b>\n\n"
        "Send <b>/ph &lt;number&gt;</b> to get details.\n"
        "Example: <b>/ph 9026927714</b>"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['ph'])
def phone_lookup(message):
    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            bot.reply_to(message, "❌ Please provide a phone number.\nExample: <b>/ph 9026927714</b>")
            return

        raw_number = args[1].replace(" ", "").strip()
        number = raw_number[-10:]  # last 10 digits

        results = fetch_number_details(number)

        if not results:
            bot.reply_to(message, "⚠️ No data found for this number.")
            return

        formatted = format_results(results)
        bot.send_message(message.chat.id, formatted)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: <code>{e}</code>")


print("✅ Bot is running...")
bot.infinity_polling()
