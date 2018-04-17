# -*- coding: utf-8 -*-
import locale
from datetime import datetime
from telebot import types


def from_string_to_datetime(string_date, fm="%Y-%m-%d %H:%M:%S.%f"):
    return datetime.strptime(string_date, fm)


def from_datetime_to_string(datetime_date, fm="%d %B/ %H:%M", rus_loc=False):
    if rus_loc:
        loc = locale.getlocale()
        locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
        datetime = datetime_date.strftime(fm)
        locale.setlocale(locale.LC_ALL, loc)
        return datetime
    return datetime_date.strftime(fm)


def getItems(text):
    t = text.split(" ")
    return t[0], t[1], t[2], t[3]


def formatItems(isOwn, array):
    text = ""
    if not array:
        return 'К сожалению пока нет записей.'
    else:
        for elem in array:
            text += "{} продает: {} \nКоличество: {} \nЦена в долларах: {}\nКомиссия в процентах: {} \n\n".format(elem[1], elem[2], elem[3], elem[4], elem[5])
    return text


def create_keyboard(words=None, width=None):
        keyboard = types.ReplyKeyboardMarkup(row_width=width, resize_keyboard=True)
        for word in words:
            keyboard.add(types.KeyboardButton(text=word))
        return keyboard


def create_inline_keyboard(orders, type=None):
        keyboard = types.InlineKeyboardMarkup()
        callback_data = 'empty'

        if type == 'deleteOrder':
            return create_inline_button_for_delete(orders)
        elif type == 'showOrder':
            return create_inline_button_for_show()
        for i in range(len(orders)):
            item_id = str(int(orders[i].split('.')[0]))
            callback_data = '{}.{}'.format(type, item_id)
            # if type == 'source':
            #     item_id = str(int(orders[i].split('.')[0]))
            #     callback_data = '{}.{}'.format(type, item_id)
            # elif type == 'destination':
            #     item_id = str(int(orders[i].split('.')[0]))
            #     callback_data = '{}.{}'.format(type, item_id)
            # elif type == 'type':
            #     item_id = str(int(orders[i].split('.')[0]))
            #     callback_data = '{}.{}'.format(type, item_id)
            # if type == 'dr_source':
            #     item_id = str(int(orders[i].split('.')[0]))
            #     callback_data = '{}.{}'.format(type, item_id)
            # if type == 'dr_destination':
            #     item_id = str(int(orders[i].split('.')[0]))
            #     callback_data = '{}.{}'.format(type, item_id)

            btn = types.InlineKeyboardButton(text=orders[i], callback_data=callback_data)
            keyboard.add(btn)
        return keyboard


def create_inline_button_for_delete(order):
    keyboard = types.InlineKeyboardMarkup()
    callback_data = 'deleteOrder.{}'.format(order[0])
    btn = types.InlineKeyboardButton(text='Удалить объявление', callback_data=callback_data)
    keyboard.add(btn)
    return keyboard


def create_inline_button_for_show():
    keyboard = types.InlineKeyboardMarkup()
    return keyboard


def create_inline_keyboard_for_html(orders):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(orders)):
        btn = types.InlineKeyboardButton(text=orders[i], callback_data=orders[i])
        keyboard.add(btn)
    return keyboard
