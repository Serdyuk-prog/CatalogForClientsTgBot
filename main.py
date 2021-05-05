import telebot
import confing
import responders

bot = telebot.TeleBot(confing.TOKEN, parse_mode=None)


MAIN_PAGE_MARKUP = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) \
    .row(telebot.types.KeyboardButton('🍭 Поиск'))\
    .row(telebot.types.KeyboardButton('🍱 Категории'),
         telebot.types.KeyboardButton('🍥 Настройки')) \
    .row(telebot.types.KeyboardButton('🍻 Помощь'),
         telebot.types.KeyboardButton('🥂 Поделиться'))


# Start
@bot.message_handler(commands=['start'])
def start_message(message: telebot.types.Message):
    # Here the bot describes about itself, what it can do and so on...
    # TODO Описать основные возможности бота
    bot.send_message(message.chat.id, "Тут то, что я могу, умею, практикую",
                     reply_markup=MAIN_PAGE_MARKUP)


# Categories
@bot.message_handler(commands=['categories'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍱 Категории")
def categories_by_button(message: telebot.types.Message):
    responders.show_categories(bot, message)


# Settings
@bot.message_handler(commands=['settings'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍥 Настройки")
def settings_by_button(message: telebot.types.Message):
    responders.show_settings(bot, message)


# Help
@bot.message_handler(commands=['help'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍻 Помощь")
def help_by_button(message: telebot.types.Message):
    responders.show_help(bot, message)


# Share
@bot.message_handler(commands=['share'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🥂 Поделиться")
def share_by_button(message: telebot.types.Message):
    responders.do_share(bot, message)


# Search
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍭 Поиск")
def search_by_markup(message: telebot.types.Message):
    # Here is a search responder...
    # TODO Изменить текст сообщения ниже
    bot.send_message(message.chat.id, "Ну ты это... и так в поиске, просто напиши мне что-нибудь и я объязательно "
                                      "найду. \r\n"
                                      "PS: Или не найду, тут как повезет")


@bot.message_handler(content_types=['text'])
def search_by_text(message: telebot.types.Message):
    responders.do_search(bot, message)


if __name__ == '__main__':
    print('bot is started')
    bot.polling()

