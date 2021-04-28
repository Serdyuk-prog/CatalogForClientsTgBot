import telebot


def do_search(bot: telebot.TeleBot, message: telebot.types.Message):
    # TODO сформировать резултат поиска в виде списка, с возможность посмотреть о продукте больше
    bot.send_message(message.chat.id, "Тут будет результат поиска")


def show_categories(bot: telebot.TeleBot, message: telebot.types.Message):
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
