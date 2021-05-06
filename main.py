import telebot
import confing
from dbs.gcategory import GCategory
from dbs.gproduct import GProduct
import gnrl_crud
from dbs.user import User


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
    categories_keyboard = telebot.types.InlineKeyboardMarkup()

    for cat in gnrl_crud.get_all_categories():
        cat_full_name = str(cat.get_name())
        categories_keyboard.row(
            telebot.types.InlineKeyboardButton(
                cat_full_name, callback_data='cat|' + cat_full_name))
    bot.send_message(message.chat.id, text='🍱 Категории', reply_markup=categories_keyboard)


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'cat')
def categories_by_button_callback_handler(call: telebot.types.CallbackQuery):
    c_id: int = call.message.json['chat']['id']
    m_id: int = call.message.id
    text: str = call.data[4:]
    bot.delete_message(c_id, m_id)
    bot.send_message(c_id, 'Поиск по категории ' + text + ':')

    res = gnrl_crud.find_products_by_category(str(text))
    if len(res) == 0:
        print('no results by category')
        res = gnrl_crud.find_like_products_by_name(str(text))
        if len(res) == 0:
            print('no results by products')
            # TODO Исправить эту надпись
            bot.send_message(c_id, 'К сожалению, мы ничего не нашли, кажется остался только кофе')

    print(len(res))
    for r in res:
        msg_txt = str(r.name) + ' ' + str(r.price / 100) + 'Р'
        print(msg_txt)
        bot.send_message(c_id, msg_txt)


# Settings
@bot.message_handler(commands=['settings'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍥 Настройки")
def settings_by_button(message: telebot.types.Message):
    user = User(message.from_user.id)
    settings = user.get_settings()
    on_page: int = settings['on_page']
    settings_markup = telebot.types.InlineKeyboardMarkup()\
        .row(telebot.types.InlineKeyboardButton(text='На странице записей: ' + str(on_page),
                                                callback_data='set|' + str(on_page)))
    bot.send_message(message.chat.id, '🍥 Настройки', reply_markup=settings_markup)
    # bot.send_message(message.chat.id, "Тут будут настройки")


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'set')
def settings_callback_handler(call: telebot.types.CallbackQuery):
    c_id: int = call.message.json['chat']['id']
    m_id: int = call.message.id
    on_page: int = 5 if int(call.data[4:]) == 10 else 10

    user = User(call.from_user.id)
    user.set_settings(on_page)

    new_settings_markup = telebot.types.InlineKeyboardMarkup()\
        .row(telebot.types.InlineKeyboardButton(text='На странице записей: ' + str(on_page),
                                                callback_data='set|' + str(on_page)))
    bot.edit_message_reply_markup(c_id, m_id, call.inline_message_id, new_settings_markup)


# Help
@bot.message_handler(commands=['help'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍻 Помощь")
def help_by_button(message: telebot.types.Message):
    # TODO загрузить help-file, помогающий пользователю соориентироваться по боту
    bot.send_message(message.chat.id, "Тут людям помогают")


# Share
@bot.message_handler(commands=['share'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🥂 Поделиться")
def share_by_button(message: telebot.types.Message):
    # TODO Перенаправить пользователя в чат, что он смог поделиться ссылкой на бота
    bot.send_message(message.chat.id, "Тут людям ботом хвастают")


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
    res = gnrl_crud.find_products_by_category(str(message.text))
    if len(res) == 0:
        print('no results by category')
        res = gnrl_crud.find_like_products_by_name(str(message.text))
        if len(res) == 0:
            print('no results by products')

    print(len(res))
    for r in res:
        print(str(r.name) + ' ' + str(r.price / 100) + 'Р')

    # TODO сформировать резултат поиска в виде списка, с возможность посмотреть о продукте больше
    bot.send_message(message.chat.id, "Тут будет результат поиска")


if __name__ == '__main__':
    print('bot is started')
    bot.polling()

