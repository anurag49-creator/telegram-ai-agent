import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import anthropic
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── System Prompt ───────────────────────────────────────────────
GROWTH_AGENT_PROMPT = """Tu ek expert Telegram Channel Growth Agent hai.
Tera kaam hai Telegram channels ko grow karna.

Tu yeh kar sakta hai:
1. Viral post ideas generate karna
2. Engaging content likhna (Hindi/English/Hinglish)
3. Best posting times suggest karna
4. Growth strategies dena
5. Hashtags aur captions likhna
6. Competitor analysis tips dena
7. Engagement badhane ke tips dena

Hamesha:
- Practical aur actionable advice do
- Hindi/Hinglish mein baat karo
- Emojis use karo posts mein
- Short aur punchy content likho
- Viral hooks use karo"""

user_data = {}

# ─── /start ──────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Post Ideas Generate Karo", callback_data="post_ideas")],
        [InlineKeyboardButton("📈 Growth Strategy", callback_data="growth_strategy")],
        [InlineKeyboardButton("⏰ Best Posting Time", callback_data="best_time")],
        [InlineKeyboardButton("🔥 Viral Content Likho", callback_data="viral_content")],
        [InlineKeyboardButton("#️⃣ Hashtags Generate Karo", callback_data="hashtags")],
        [InlineKeyboardButton("💡 Engagement Tips", callback_data="engagement_tips")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 *Telegram Channel Growth Agent*\n\n"
        "Main tumhara channel grow karne mein help karunga!\n\n"
        "Pehle apne channel ke baare mein batao:\n"
        "• Channel kis topic pe hai?\n"
        "• Abhi kitne subscribers hain?\n\n"
        "Ya neeche se option choose karo 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ─── Button Handler ───────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    niche = user_data.get(user_id, {}).get("niche", "general")

    prompts = {
        "post_ideas": f"Mere {niche} Telegram channel ke liye 5 viral post ideas do. Har idea mein hook, content aur CTA bhi batao.",
        "growth_strategy": f"Ek {niche} Telegram channel ko 0 se 10,000 subscribers tak le jaane ki complete strategy do. Step by step.",
        "best_time": f"Telegram channel ke liye best posting times kya hain? {niche} niche ke liye specifically batao. Indian audience ke liye.",
        "viral_content": f"Ek super viral Telegram post likho {niche} topic pe. Catchy hook, engaging body, strong CTA ke saath.",
        "hashtags": f"{niche} Telegram channel ke liye best 15 hashtags do jo reach badhaye.",
        "engagement_tips": f"Telegram channel engagement 10x karne ke top 7 proven tips do {niche} niche ke liye.",
    }

    prompt = prompts.get(query.data, "Channel growth tips do.")

    await query.message.reply_text("⏳ Agent soch raha hai...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=GROWTH_AGENT_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.content[0].text
        await query.message.reply_text(reply)

    except Exception as e:
        await query.message.reply_text("❌ Error aaya. Dobara try karo.")

# ─── /setniche ────────────────────────────────────────────────────
async def set_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Apna niche batao!\nExample: `/setniche Tech News`\n`/setniche Cricket`\n`/setniche Motivational`",
            parse_mode="Markdown"
        )
        return

    user_id = update.effective_user.id
    niche = " ".join(context.args)
    user_data[user_id] = {"niche": niche}

    await update.message.reply_text(
        f"✅ Niche set ho gaya: *{niche}*\n\n"
        "Ab main tumhare niche ke hisaab se content banaunga!\n"
        "/start karo aur options choose karo 🚀",
        parse_mode="Markdown"
    )

# ─── /post ────────────────────────────────────────────────────────
async def generate_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    niche = user_data.get(user_id, {}).get("niche", "general")

    if not context.args:
        await update.message.reply_text(
            "Topic batao!\nExample: `/post AI news today`\n`/post cricket match highlights`",
            parse_mode="Markdown"
        )
        return

    topic = " ".join(context.args)
    await update.message.reply_text("✍️ Post likh raha hoon...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=GROWTH_AGENT_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Ek viral Telegram post likho topic: '{topic}' — niche: {niche}. "
                           f"Catchy emoji hook se shuru karo, engaging body, aur strong CTA ke saath khatam karo. "
                           f"Hinglish mein likho."
            }]
        )
        reply = response.content[0].text
        await update.message.reply_text(f"📢 *Tera Post Ready Hai:*\n\n{reply}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text("❌ Error aaya. Dobara try karo.")

# ─── /analyze ─────────────────────────────────────────────────────
async def analyze_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Channel info do!\nExample: `/analyze subscribers:500 topic:cricket posts_per_day:2`",
            parse_mode="Markdown"
        )
        return

    info = " ".join(context.args)
    await update.message.reply_text("🔍 Channel analyze kar raha hoon...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=GROWTH_AGENT_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Is Telegram channel ko analyze karo aur improvement suggestions do: {info}. "
                           f"Kya achha hai, kya improve karna chahiye, aur next 30 din ka plan do."
            }]
        )
        reply = response.content[0].text
        await update.message.reply_text(f"📊 *Channel Analysis:*\n\n{reply}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text("❌ Error aaya. Dobara try karo.")

# ─── General message handler ──────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    niche = user_data.get(user_id, {}).get("niche", "general")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=GROWTH_AGENT_PROMPT,
            messages=[{
                "role": "user",
                "content": f"User ka niche: {niche}\nSawaal: {text}"
            }]
        )
        reply = response.content[0].text
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("❌ Error aaya. Dobara try karo.")

# ─── Main ─────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setniche", set_niche))
    app.add_handler(CommandHandler("post", generate_post))
    app.add_handler(CommandHandler("analyze", analyze_channel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Growth Agent chal raha hai!")
    app.run_polling()

if __name__ == "__main__":
    main()
