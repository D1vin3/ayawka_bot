# -*- coding: utf-8 -*-
import emoji


# Main Buttons when bot /start/
main_buttons = [
    '{} Купить'.format(emoji.emojize(':shopping_cart:')),
    '{} Продать'.format(emoji.emojize(':money_bag:', use_aliases=True)),
    '{} Мои_объявления'.format(emoji.emojize(':package:', use_aliases=True))
]

reset_buttons = [
    'Главная'
]

main_buttons_without_img = [
    '/Отправить_посылку',
    '/Могу_доставить',
    '/Мои_объявления'
]

source_buttons = [
    '1. Алматы',
    '2. Астана',
    '3. Шымкент',
    '4. Караганда',
    '5. Актобе',
]

destination_buttons = [
    '1. Алматы',
    '2. Астана',
    '3. Шымкент',
    '4. Караганда',
    '5. Актобе',
]

from_to_locations_buttons = [
    '1. Алматы-Астана',
    '2. Астана-Алматы',
]

travel_types_buttons = [
    '1. Самолёт',
    '2. Поезд'
]

currency_site_buttons = [
    '1. blockchain.info',
    '2. bittrex.com',
    '3. bitfinex.com',
    '4. poloniex.com',
    '5. exmo.com',
    '6. cex.io',
    '7. yobit.net',
    '8. Другой',
]

currency_site_buttons_html = [
    '<a>blockchain.info</a>',
    # '<a href="http://bittrex.com">bittrex.com</a>',
    # '<a href="http://bitfinex.com">bitfinex.com</a>'
    # '<a href="http://blockchain.info">blockchain.info</a>',
    # '<a href="http://blockchain.info">blockchain.info</a>',
    # '<a href="http://blockchain.info">blockchain.info</a>',
    # '<a href="http://blockchain.info">blockchain.info</a>',
    # '<a href="http://blockchain.info">blockchain.info</a>',
]

marginality_amount_buttons = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'более 10']
