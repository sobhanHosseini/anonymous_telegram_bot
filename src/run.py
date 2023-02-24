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
            """
             /start command handler
            """
            self.send_message(
                message.chat.id, 
                f'Hey <strong>{message.chat.first_name}</strong>',
                reply_markup=self.keyboards.main,
                )
           
            message.json['_id'] = message.chat.id
            db.users.update_one(
                {'_id': message.chat.id}, 
                {"$set": message.json},
                upsert=True
                )
            self.update_state(message.chat.id, self.states.main)
            
        @self.bot.message_handler(regexp=emoji.emojize(self.keys.random_connect))
        def random_connect(message):
            """
            Randomly connect to another user
            """
            self.send_message_update_state(
                chat_id=message.chat.id,
                text=':busts_in_silhouette: Connecting you to a random stranger...',
                reply_markup=self.keyboards.exit,
                state=self.states.random_connect
                )
            
            other_user = self.find_user(
                condition={
                    'state': self.states.random_connect,
                    '_id': {'$ne': message.chat.id}
                }
            )
      
            if not other_user:
                return
      
            # coneccted two stranger
            self.conected_two_starnger(first_user_id=message.chat.id, second_user_id=other_user["_id"])
            print('here........')
    
        @self.bot.message_handler(regexp=emoji.emojize(self.keys.exit))
        def exit(message):
            """
            exit from chat or connection state
            """
            # update current user
            self.send_message_update_state(
                chat_id=message.chat.id,
                text=self.keys.exit,
                reply_markup=self.keyboards.main,
                state=self.states.main
                )
            
            # get connected to user
            connected_to = self.find_user(message.chat.id)

            if not connected_to.get('connected_to'):
                return
            
            # update connected to user state and terminate the connection  
            other_chat_id = connected_to['connected_to']
            
            self.send_message_update_state(
                chat_id=other_chat_id,
                text=self.keys.exit,
                reply_markup=self.keyboards.main,
                state=self.states.main
                )
            
            # remove connected users
            self.update_connected_status(chat_id=message.chat.id, connected_to=None)
            
            self.update_connected_status(chat_id=other_chat_id, connected_to=None)
             
        @self.bot.message_handler(is_admin=True)
        def admin_of_group(message):
            self.send_message(
                message.chat.id,
                '<strong> You are admin of this chat! </strong>'
                )
        
        @self.bot.message_handler(func=lambda _: True)
        def echo(message):
            """
            Echo message to other user
            """
            user = self.find_user(message.chat.id)
            
            if (not user or user['state'] != self.states.connected or user['connected_to'] is None):
                return
            
            self.send_message(
                user['connected_to'],
                message.text
            )
    
    def conected_two_starnger(first_user_id, second_user_id):
        """
        connected two stranger.
        """
        print('in conected two stranger.....')
        return
        # update fiest user state
        self.send_message_update_state(
            chat_id=first_user_id,
            text=f'Connected to {second_user_id} ....',
            state=self.states.connected
            )
        
        # update second user state
        self.send_message_update_state(
            chat_id=second_user_id,
            text=f'Connected to {first_user_id} ....',
            state=self.states.connected
            )
        
        # store first connected users
        self.update_connected_status(chat_id=first_user_id, connected_to=second_user_id)
        
        # store second connected user
        self.update_connected_status(chat_id=second_user_id, connected_to=first_user_id)
        
    
    def update_connected_status(self, chat_id, connected_to=None):
        """
        update conected_to status
        """
        db.users.update_one(
                {'_id': chat_id},
                {'$set': {'connected_to': connected_to}}
            )
    
    def send_message_update_state(self, chat_id, text, reply_markup, state):
        """
        send message and change state of user
        """
        self.send_message(
                chat_id,
                text,
                reply_markup=reply_markup
                )
        self.update_state(chat_id, state)
        
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
    
    def find_user(self, id=None, condition=None):
        default = {'_id': id}
        
        if condition != None:
            default.update(condition)
            
        return db.users.find_one(default)
        
        
if __name__ == '__main__':
    logger.info('Bot Started')
    anonymous_bot = Bot(telebot=bot)
    anonymous_bot.run()