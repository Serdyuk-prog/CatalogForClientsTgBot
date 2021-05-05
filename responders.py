import telebot
from dbs.gcategory import GCategory
from dbs.gproduct import GProduct
import gnrl_crud


def do_search(bot: telebot.TeleBot, message: telebot.types.Message):
    res = gnrl_crud.find_products_by_category(str(message.text))
    if len(res) == 0:
        print('no results by category')
        res = gnrl_crud.find_like_products_by_name(str(message.text))
        if len(res) == 0:
            print('no results by products')

    print(len(res))
    for r in res:
        print(str(r.name) + ' ' + str(r.price/100) + 'Р')

    # TODO сформировать резултат поиска в виде списка, с возможность посмотреть о продукте больше
    bot.send_message(message.chat.id, "Тут будет результат поиска")


def show_categories(bot: telebot.TeleBot, message: telebot.types.Message):

    for cat in gnrl_crud.get_all_categories():
        bot.send_message(message.chat.id, cat.get_name())

    # TODO Сформировать список возможных продуктов: (хлебобулочные, молочные...), inline_buttons!!!
    bot.send_message(message.chat.id, "Тут будет список категорий")


def show_settings(bot: telebot.TeleBot, message: telebot.types.Message):
    # TODO Сформировать inline_buttons для настроек (количество записей на странице при поиске)
    bot.send_message(message.chat.id, "Тут будут настройки")


def show_help(bot: telebot.TeleBot, message: telebot.types.Message):
    # TODO загрузить help-file, помогающий пользователю соориентироваться по боту
    bot.send_message(message.chat.id, "Тут людям помогают")


def do_share(bot: telebot.TeleBot, message: telebot.types.Message):
    # TODO Перенаправить пользователя в чат, что он смог поделиться ссылкой на бота
    bot.send_message(message.chat.id, "Тут людям ботом хвастают")
