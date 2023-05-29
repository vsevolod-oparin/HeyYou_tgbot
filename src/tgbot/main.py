#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
import sys
sys.path.append('.')

import argparse
import logging

from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.tgbot.utils import get_joined_lines, get_file_content, htmlify

from src.tgbot.youchat import YouChatInterface

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

HELP_MESSAGE = get_joined_lines(get_file_content(Path('src/messages/en/help.txt')))
INTRO_MESSAGE = get_joined_lines(get_file_content(Path('src/messages/en/intro.txt')))


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html(HELP_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_html(HELP_MESSAGE)


async def intro_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html(INTRO_MESSAGE)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sample training script")
    parser.add_argument("--telegram_token_path", default='src/tokens/telegram', help="Path to telegram token")
    parser.add_argument("--betterapi_key_path", default='src/tokens/betterapi', help="Path to betterapi API key")
    parser.add_argument("--query_queue_threshold", default=10, type=int, help="Query line threshold to give a warning message")
    return parser


def main() -> None:
    """Start the bot."""

    args = get_parser().parse_args()

    telegram_token = get_file_content(Path(args.telegram_token_path))
    betterapi_key = get_file_content(Path(args.betterapi_key_path))

    application = Application.builder().token(telegram_token).concurrent_updates(True).build()
    youchat_interface = YouChatInterface(
        api_key=betterapi_key,
        logger=logger,
        query_queue_threshold=args.query_queue_threshold,
    )

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("intro", intro_command))
    application.add_handler(CommandHandler(youchat_interface.cmd_prefix, youchat_interface.telegram_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, youchat_interface.process_noncmd_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
