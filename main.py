import telebot
import gnrl_crud
import jcrud

from dbs.gcategory import GCategory
from dbs.gproduct import GProduct
from dbs.user import User


token = jcrud.read_token()
bot = bot = telebot.TeleBot(token, parse_mode=None)




MAIN_PAGE_MARKUP = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) \
    .row(telebot.types.KeyboardButton('🍭 Поиск'))\
    .row(telebot.types.KeyboardButton('🍱 Категории'),
         telebot.types.KeyboardButton('🍥 Настройки')) \
    .row(telebot.types.KeyboardButton('🍻 Помощь'),
         telebot.types.KeyboardButton('🥂 Поделиться'))


# Start
@bot.message_handler(commands=['start'])
def start_message(message: telebot.types.Message):
    User(message.from_user.id)
    bot.send_message(message.chat.id, "Привет, приятно познакомиться",
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
        res = gnrl_crud.find_like_products_by_name(str(text))

    show_results(call.from_user.id, c_id, res)


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
    desc = jcrud.read_description()
    bot.send_message(message.chat.id, desc)


# Share
@bot.message_handler(commands=['share'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🥂 Поделиться")
def share_by_button(message: telebot.types.Message):
    # TODO Перенаправить пользователя в чат, что он смог поделиться ссылкой на бота
    share_text = jcrud.read_about()
    share_markup = telebot.types.InlineKeyboardMarkup()\
        .row(telebot.types.InlineKeyboardButton('Перешли меня', switch_inline_query=share_text))

    bot.send_message(message.chat.id, "🥂 Поделиться", reply_markup=share_markup)


# Search
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍭 Поиск")
def search_by_markup(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Ты уже в режиме поиска, просто напиши мне что-нибудь и я попробую найти")


@bot.message_handler(content_types=['text'])
def search_by_text(message: telebot.types.Message):
    res = gnrl_crud.find_products_by_category(str(message.text))
    if len(res) == 0:
        res = gnrl_crud.find_like_products_by_name(str(message.text))
    show_results(message.from_user.id, message.chat.id, res)


def show_results(u_id: int, chat_id: int, res: list[GProduct]):
    if len(res) == 0:
        # TODO Исправить эти надписи
        print('no results found')
        bot.send_message(chat_id, 'К сожалению, мы ничего не нашли, кажется остался только кофе')

    # TODO сформировать резултат поиска в виде списка, с возможность посмотреть о продукте больше
    for r in res:
        text_amount = ''
        amount_div = r.amount / r.uly_bring
        if r.amount == 0:
            text_amount = 'Нет в наличии'
        elif amount_div < 0.3:
            text_amount = 'Мало'
        elif amount_div < 0.7:
            text_amount = 'Достаточно'
        else:
            text_amount = 'Много'

        msg_txt = 'Название:' + str(r.name) + '\r\n' + \
                  'Описание:' + str('Не указано' if r.desc is None else r.desc) + '\r\n' + \
                  str('' if r.quantity is None else r.quantity + '\r\n') + \
                  'Наличие: ' + text_amount + '\r\n' + \
                  'Цена: ' + str(r.price / 100) + 'Р'

        bot.send_message(chat_id, msg_txt)


if __name__ == '__main__':
    if token is None:
        print('config file is not found')
    else:
        token = None
        print('bot is started')
        bot.polling()