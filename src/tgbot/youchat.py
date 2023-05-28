import asyncio
import random
from logging import Logger

import aiohttp as aiohttp
import urllib.parse

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.tgbot.utils import htmlify, CounterVar, Counter

QUIT_PHRASE = "I don't love you anymore, bot"

RANDOM_PHRASES = [
    'Aye, captain?',
    'Yes, sire?',
    "I'm here!",
]
ADVICE = "Psst, to query something just type `/{} <query text>`\."


class YouChatInterface:

    def __init__(self,
                 api_key: str,
                 logger: Logger,
                 max_input_length: int = 1024,
                 max_output_length: int = 3500,
                 query_queue_threshold: int = 10):
        self.api_key = api_key
        self.logger = logger
        self.query_queue_threshold = query_queue_threshold
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length

        self.cmd_prefix = 'heyyou'
        self.request_counter = CounterVar()
        self.semaphore = asyncio.Semaphore(value=1)

    async def get_response(self, query_text):
        safe_query_text = urllib.parse.quote_plus(query_text)
        url = f"https://api.betterapi.net/youchat?inputs={safe_query_text}&key={self.api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    json = await response.json()
        except:
            return "Something went wrong with API. Try another time."

        self.logger.info(json)
        if json is not None and 'status_code' in json and json['status_code'] == 200:
            return json["generated_text"]
        else:
            if json is None:
                return "Error on API side. No response provided."
            elif 'status_code' in json:
                return "Error on API side. Reponse is malformed."
            else:
                return f"Error on API side. Code error is {json['status_code']}"

    async def process_request(self, query_text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(query_text) > self.max_input_length:
            await update.message.reply_text(
                "Sorry, I can't process requests longer than {max_length}. "
                "The request you provided is {len(query_text} characters long."
            )
            return
        with Counter(self.request_counter) as _:
            if self.request_counter.val > self.query_queue_threshold:
                await update.message.reply_text(
                    f"So sorry, I need some time. Having lots of queries in the queue.",
                    reply_to_message_id=update.message.id,
                )
            async with self.semaphore:
                you_chat_response = await self.get_response(query_text)
            await update.message.reply_html(
                f'<i>YouChat says:</i>\n\n{htmlify(you_chat_response[:self.max_output_length])}',
                reply_to_message_id=update.message.id,
            )
            for i in range(self.max_output_length, len(you_chat_response), self.max_output_length):
                await update.message.reply_html(
                    htmlify(you_chat_response[i:i + self.max_output_length]),
                )

    async def telegram_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query_text = update.message.text[len(self.cmd_prefix) + 1:].strip()
        if QUIT_PHRASE in query_text:
            await update.message.reply_text('My heart is broken...')
            await update.message.chat.leave()
            return
        if query_text == '':
            await update.message.reply_text(random.choice(RANDOM_PHRASES))
            await asyncio.sleep(1.0)
            await update.message.reply_text(ADVICE.format(self.cmd_prefix), parse_mode='MarkdownV2')
            return
        await self.process_request(query_text, update, context)

    async def process_noncmd_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text
        bot_username = context.bot.username
        if update.message.chat.type == 'private' or bot_username in message_text:
            query_text = message_text.replace(bot_username, '').strip()
            await self.process_request(query_text, update, context)


