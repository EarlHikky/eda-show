"""
This module contains the implementation of the bot.
"""

import logging

from os import getenv
from asyncio import sleep

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from random_recipe import get_random_recipe_async


async def get_url(recipe_type: str | None = None) -> str:
    _, recipe = await get_random_recipe_async(recipe_type)
    url = recipe["url"]
    return url


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE, buttons) -> None:
    chat_id = update.effective_chat.id
    sent_messages = list()
    with open("./kelso.jpg", "rb") as photo:
        sent_messages.append(await update.message.reply_photo(photo=photo))

    await update.message.delete()

    sent_messages.append(await update.message.reply_text(
        "Here you go, sport",
        reply_markup=ReplyKeyboardMarkup.from_row(
            buttons,
            one_time_keyboard=True
        ),
    )
                         )

    await sleep(20)

    try:
        for sent_message in sent_messages:
            await context.bot.delete_message(chat_id=chat_id, message_id=sent_message.message_id)
    except Exception as e:
        logging.info(f"Не удалось удалить сообщение: {e}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    buttons = [
        KeyboardButton(
            text="Завтрак",
            web_app=WebAppInfo(url=await get_url("Breakfast")),
        ),
        KeyboardButton(
            text="Обед",
            web_app=WebAppInfo(url=await get_url("Dinner"))
        ),
        KeyboardButton(
            text="Ужин",
            web_app=WebAppInfo(url=await get_url("Dinner"))
        ),
        KeyboardButton(
            text="Десерт",
            web_app=WebAppInfo(url=await get_url("Dessert"))
        ),

    ]
    await answer(update, context, buttons)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens the web app."""
    url = await get_url()
    buttons = [KeyboardButton(text="Мне повезёт!", web_app=WebAppInfo(url=url))]
    await answer(update, context, buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("/random - рандомная рецепта\n/choose - выбрать рецепт")
    await update.message.delete()


def main() -> None:
    """Start the bot."""
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        filename="log.log",
        filemode="w",
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    load_dotenv()
    token = getenv("BOT_TOKEN", None)
    if not token:
        exit("Please, set BOT_TOKEN environment variable!")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("random", random))
    application.add_handler(CommandHandler("choose", echo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
