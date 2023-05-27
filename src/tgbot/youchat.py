import requests
import urllib.parse

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


QUIT_PHRASE = "I don't love you anymore, bot..."


class YouChatInterface:

    def __init__(self, api_key: str, max_input_length: int = 1024, max_output_length: int = 3500):
        self.api_key = api_key
        self.cmd_prefix = 'heyyou'
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length

    def get_response(self, query_text):
        safe_query_text = urllib.parse.quote_plus(query_text)
        url = f"https://api.betterapi.net/youchat?inputs={safe_query_text}&key={self.api_key}"
        try:
            json = requests.get(url).json()  # load json form api
        except:
            return "Something went wrong with API. Try another time."

        print(json)
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
        you_chat_response = self.get_response(query_text)
        await update.message.reply_text(
            f'YouChat says:\n\n{you_chat_response[:self.max_output_length]}',
            reply_to_message_id=update.message.id,
        )
        for i in range(self.max_output_length, len(you_chat_response), self.max_output_length):
            await update.message.reply_text(
                you_chat_response[i:i + self.max_output_length],
            )


    async def telegram_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query_text = update.message.text[len(self.cmd_prefix) + 1:].strip()
        if QUIT_PHRASE in query_text:
            await update.message.reply_text('My heart is broken...')
            await update.message.chat.leave()
            return
        await self.process_request(query_text, update, context)

    async def process_noncmd_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text
        bot_username = context.bot.username
        if update.message.chat.type == 'private' or bot_username in message_text:
            query_text = message_text.replace(bot_username, '').strip()
            await self.process_request(query_text, update, context)


