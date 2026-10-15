import logging
import os
from uuid import uuid4
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
)

# Enable logging for tracking status on Render
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Sample Movie Database
MOVIES = {
    "inception": {
        "title": "Inception (2010)",
        "genre": "Sci-Fi / Action",
        "rating": "8.8/10",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "about": "Directed by Christopher Nolan, starring Leonardo DiCaprio. A masterpiece of mind-bending cinema."
    },
    "interstellar": {
        "title": "Interstellar (2014)",
        "genre": "Sci-Fi / Drama",
        "rating": "8.7/10",
        "description": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot is tasked to pilot a spacecraft to find a new planet for humans.",
        "about": "Directed by Christopher Nolan, featuring an iconic score by Hans Zimmer."
    },
    "the dark knight": {
        "title": "The Dark Knight (2008)",
        "genre": "Action / Crime",
        "rating": "9.0/10",
        "description": "When the menace known as the Joker wreaks havoc and chaos on Gotham, Batman must accept one of the greatest psychological and physical tests.",
        "about": "Directed by Christopher Nolan, featuring Heath Ledger's legendary Academy Award-winning performance."
    },
    "parasite": {
        "title": "Parasite (2019)",
        "genre": "Drama / Thriller",
        "rating": "8.5/10",
        "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        "about": "Directed by Bong Joon Ho. The first non-English language film to win Best Picture."
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎬 *Welcome to MovieRec Bot!*\n\n"
        "I can recommend top-rated movies, give you detailed synopses, and work inline anywhere!\n\n"
        "✨ *Commands:*\n"
        "• /movies - View featured list\n"
        "• /about - Bot info & compliance\n"
        "• Type `@YourBotUsername <movie>` in *any chat* for instant inline recommendations!"
    )
    keyboard = [
        [InlineKeyboardButton("🎥 View Movies", callback_data="show_movies")],
        [InlineKeyboardButton("ℹ️ About Bot", callback_data="show_about")]
    ]
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = (
        "ℹ️ *About MovieRec Bot*\n\n"
        "A streamlined movie recommendation service built with Python and deployed securely on Render as a background worker.\n\n"
        "🛡 *Platform Compliance:* Operates transparently in compliance with Telegram bot terms. Safe for general groups and channels."
    )
    if update.message:
        await update.message.reply_text(about_text, parse_mode="Markdown")

async def movies_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "📋 *Featured Movie List:*\n\n"
    for key, m in MOVIES.items():
        text += f"• *{m['title']}* ({m['genre']}) — `/get_{key}`\n"
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")

async def get_movie_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    movie_key = text.replace("/get_", "").strip().lower()
    
    if movie_key in MOVIES:
        m = MOVIES[movie_key]
        response = (
            f"🎬 *{m['title']}*\n"
            f"⭐ *Rating:* {m['rating']} | *Genre:* {m['genre']}\n\n"
            f"📝 *Synopsis:* {m['description']}\n\n"
            f"💡 *About:* {m['about']}"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("Movie not found. Use /movies to see options.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_movies":
        text = "📋 *Featured Movies:*\n"
        for key, m in MOVIES.items():
            text += f"• *{m['title']}* — `/get_{key}`\n"
        await query.edit_message_text(text, parse_mode="Markdown")
    elif query.data == "show_about":
        await query.edit_message_text("ℹ️ Powered by Python & Render Background Worker infrastructure.", parse_mode="Markdown")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enables inline search mode in any chat via @BotUsername"""
    query = update.inline_query.query.strip().lower()
    results = []

    for key, m in MOVIES.items():
        if not query or query in key or query in m["title"].lower() or query in m["genre"].lower():
            content = (
                f"🎬 *{m['title']}*\n"
                f"⭐ *Rating:* {m['rating']} | *Genre:* {m['genre']}\n\n"
                f"📝 *Synopsis:* {m['description']}\n\n"
                f"💡 *About:* {m['about']}"
            )
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=m["title"],
                    description=f"{m['genre']} - ⭐ {m['rating']}",
                    input_message_content=InputTextMessageContent(content, parse_mode="Markdown"),
                )
            )

    await update.inline_query.answer(results, cache_time=5)

def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.error("Missing BOT_TOKEN environment variable.")
        return

    application = ApplicationBuilder().token(token).build()

    # Handlers Registration
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("movies", movies_command))
    for key in MOVIES.keys():
        application.add_handler(CommandHandler(f"get_{key}", get_movie_detail))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(InlineQueryHandler(inline_query))

    logger.info("Bot started successfully in polling mode...")
    application.run_polling()

if __name__ == "__main__":
    main()
