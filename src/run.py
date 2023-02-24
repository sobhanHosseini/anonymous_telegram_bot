import os

import telebot
from loguru import logger

from src.dataClass import keyboards as kb
from src.bot import bot
from src.filters import IsAdmin
import emoji
from src.db import db

class Bot:
    """
    Telegram bot to randomly connect two strangers to talk!
    """
    def __init__(self, telebot):
        self.bot = telebot
        
        # add custom filters
        self.bot.add_custom_filter(IsAdmin())
        
        # register handlers
        self.handlers()
        
    def run(self):
        # run bot 
        logger.info('Bot is running...')
        self.bot.infinity_polling()
        
    def handlers(self):
        
        @self.bot.message_handler(commands=['start'])    
        def start(message):
            self.send_message(
                message.chat.id, 
                f'Hey "<strong>{message.chat.first_name}</strong>"'
                )
           
            # db.users.insert_one(
            #     #{'chat.id': message.chat.id},
            #     {message.json},
            #     )
            # message.json['chat.id'] = message.chat.id
            a = db.users.insert_one({"_id": message.chat.id}, {"$set": message.json}, upsert=True)
            print(a)
             
        @self.bot.message_handler(is_admin=True)
        def admin_of_group(message):
            self.send_message(message.chat.id, '<strong> You are admin of this chat! </strong>')
        
        @self.bot.message_handler(func=lambda _: True)
        def echo(message):
            keyboards = kb.Keyboards() 
            
            self.send_message(
                message.chat.id,
                message.text,
                reply_markup=keyboards.main
                )
        
    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        if emojize:
            text = emoji.emojize(text)
        
        self.bot.send_message(chat_id, text, reply_markup=reply_markup)
		
if __name__ == '__main__':
	logger.info('Bot Started')
	anonymous_bot = Bot(telebot=bot)
	anonymous_bot.run()