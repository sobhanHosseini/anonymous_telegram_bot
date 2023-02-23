import os

import telebot
from loguru import logger

from src.dataClass import keyboards as kb
from src.utils.io import write_json


class Bot:
    """
    Template for telegram bot.
    """
    def __init__(self) -> None:
        self.bot = telebot.TeleBot(os.environ['ANONYMOUS_BOT_TOKEN'])
        self.echo_all = self.bot.message_handler(func=lambda message: True)(self.echo_all)
    
    def run(self):
        logger.info('Bot is running...')
        self.bot.infinity_polling()
    
    def echo_all(self, message):
        keyboards = kb.Keyboards() 
        
        self.bot.send_message(
            message.chat.id, message.text,
            reply_markup=keyboards.main
            )
		
if __name__ == '__main__':
	logger.info('Bot Started')
	bot = Bot()
	bot.run()