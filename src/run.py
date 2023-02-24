import os

import emoji
import telebot
from loguru import logger

from src.bot import bot
from src.dataClass import keyboards as kb
from src.dataClass import keys
from src.db import db
from src.filters import IsAdmin
from src.dataClass import states


class Bot:
    """
    Telegram bot to randomly connect two strangers to talk!
    """
    def __init__(self, telebot):
        self.bot = telebot
        
        # init data class
        self.keys = keys.Keys()
        self.keyboards = kb.Keyboards()
        self.states = states.States()
         
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
                f'Hey <strong>{message.chat.first_name}</strong>'
                )
           
            message.json['_id'] = message.chat.id
            db.users.update_one(
                {'_id': message.chat.id}, 
                {"$set": message.json},
                upsert=True
                )
            self.update_state(message.chat.id, states.idle)
            
        @self.bot.message_handler(
            regexp=emoji.emojize(self.keys.random_connect)
            )
        def random_connect(message):
            self.send_message(
                message.chat.id,
                ':busts_in_silhouette: Connecting you to a random stranger...',
                reply_markup=self.keyboards.exit
                )
            self.update_state(message.chat.id, self.states.random_connect)
             
        @self.bot.message_handler(is_admin=True)
        def admin_of_group(message):
            self.send_message(
                message.chat.id,
                '<strong> You are admin of this chat! </strong>'
                )
        
        @self.bot.message_handler(func=lambda _: True)
        def echo(message):
            self.send_message(
                message.chat.id,
                message.text,
                reply_markup=self.keyboards.main
                )
        
    def send_message(self, chat_id, text, reply_markup=None, emojize=True):
        if emojize:
            text = emoji.emojize(text)
        
        self.bot.send_message(chat_id, text, reply_markup=reply_markup)
    
    def update_state(self, chat_id, state):
        """
        Update user state.
        """
        db.users.update_one(
            {'_id': chat_id}, 
            {'$set':{'state':state}}
            )
        
        
if __name__ == '__main__':
    logger.info('Bot Started')
    anonymous_bot = Bot(telebot=bot)
    anonymous_bot.run()