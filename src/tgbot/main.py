#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
import sys
sys.path.append('.')

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.tgbot.youchat import YouChatInterface

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


HELP_MESSAGE = '''
Hi, my name HeyYou bot. I'm a bot to query YouChat via telegram. You can talk to me in private and also get my service in the chat.

- In private chat, just talk to me.
- For public chat, use the command /heyyou. Or I admins allow, you can just tag me in your query.

To get this message again, just use /help.

For chat admins. If you want to be served in the chat by /heyyou command, just add me to the chat. If you want to get my service by tagging, add me in the chat as an admin. I don't need any permission, so feel free to disable all of them. 
'''.strip()

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode='Markdown',
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_html(HELP_MESSAGE)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def you_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(
        update.message.text,
        reply_to_message_id=update.message.id,
        parse_mode="MarkdownV2",
    )




def get_token(token_path: Path) -> str:
    with open(token_path) as f:
        return f.read()


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    path_to_tg_token = Path("/home/smileijp/projects/tgbots/HeyYou/src/tokens/telegram")
    path_to_api_token = Path("/home/smileijp/projects/tgbots/HeyYou/src/tokens/betterapi")

    application = Application.builder().token(get_token(path_to_tg_token)).build()
    youchat_interface = YouChatInterface(get_token(path_to_api_token))

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler(youchat_interface.cmd_prefix, youchat_interface.telegram_command))
    application.add_handler(CommandHandler("echo", you_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, youchat_interface.process_noncmd_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
