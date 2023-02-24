from dataclasses import dataclass
from typing import Tuple

import emoji
from telebot import types

from src.dataClass import keys

keys = keys.Keys()

def create_keyboard(*keys, row_width=2, resize_keyboard=True):
    markup =  types.ReplyKeyboardMarkup(
        row_width=row_width,
        resize_keyboard=resize_keyboard
    )
    
    keys = map(emoji.emojize, keys)
    buttons = map(types.KeyboardButton, keys)
    markup.add(*buttons)
    
    return markup

@dataclass
class Keyboards:
    main:Tuple = create_keyboard(keys.random_connect, keys.setting)
    exit:Tuple = create_keyboard(keys.exit)


