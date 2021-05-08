import telebot
import gnrl_crud
import jcrud
import json

from dbs.gcategory import GCategory
from dbs.gproduct import GProduct
from dbs.user import User

token = jcrud.read_token()
bot = telebot.TeleBot(token, parse_mode=None)

MAIN_PAGE_MARKUP = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) \
    .row(telebot.types.KeyboardButton('🍭 Поиск')) \
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

    show_results(call.from_user.id, c_id, text)


# Settings
@bot.message_handler(commands=['settings'])
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍥 Настройки")
def settings_by_button(message: telebot.types.Message):
    user = User(message.from_user.id)
    settings = user.get_settings()
    on_page: int = settings['on_page']
    settings_markup = telebot.types.InlineKeyboardMarkup() \
        .row(telebot.types.InlineKeyboardButton(text='На странице записей: ' + str(on_page),
                                                callback_data='set|' + str(on_page)))
    bot.send_message(message.chat.id, '🍥 Настройки', reply_markup=settings_markup)
    # bot.send_message(message.chat.id, "Тут будут настройки")


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'set')
def settings_callback_handler(call: telebot.types.CallbackQuery):
    c_id: int = call.message.json['chat']['id']
    m_id: int = call.message.id
    on_page: int = 1 if int(call.data[4:]) == 2 else 2

    user = User(call.from_user.id)
    user.set_settings(on_page)

    new_settings_markup = telebot.types.InlineKeyboardMarkup() \
        .row(telebot.types.InlineKeyboardButton(text='На странице записей: ' + str(on_page),
                                                callback_data='set|' + str(on_page)))
    try:
        bot.edit_message_reply_markup(c_id, m_id, call.inline_message_id, new_settings_markup)
    except Exception as e:
        print('settings_callback_handler: ' + str(e))


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
    share_text = jcrud.read_about()
    share_markup = telebot.types.InlineKeyboardMarkup() \
        .row(telebot.types.InlineKeyboardButton('Перешли меня', switch_inline_query=share_text))

    bot.send_message(message.chat.id, "🥂 Поделиться", reply_markup=share_markup)


# Search
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🍭 Поиск")
def search_by_markup(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Ты уже в режиме поиска, просто напиши мне что-нибудь и я попробую найти")


@bot.message_handler(content_types=['text'])
def search_by_text(message: telebot.types.Message):
    show_results(message.from_user.id, message.chat.id, message.text)


def show_results(user_id: int, chat_id: int, text: str):
    user = User(user_id)
    user.reset_search()

    user.set_search({'query': text})

    res, res_markup = get_search_res_n_markup(user, text)
    if len(res) == 0:
        # TODO Исправить эти надписи
        print('no results found')
        bot.send_message(chat_id, 'К сожалению, мы ничего не нашли, кажется остался только кофе')
    else:
        bot.send_message(chat_id, 'Сортировка:', reply_markup=get_sort_message_markup(user))
        bot.send_message(chat_id, 'Количество резулльтатов: ' + str(len(res)),
                         reply_markup=res_markup)


def get_sort_message_markup(user: User):
    sort = user.get_search()['sort']

    name_sign = ''
    price_sign = ''
    amount_sign = ''

    if sort == 0:
        name_sign = '🔽'
    elif sort == 1:
        price_sign = '🔽'
    elif sort == 2:
        amount_sign = '🔽'
    elif sort == 3:
        name_sign = '🔼'
    elif sort == 4:
        price_sign = '🔼'
    elif sort == 5:
        amount_sign = '🔼'

    callback_data = ['srt', str(sort)]
    sorting_markup = telebot.types.InlineKeyboardMarkup() \
        .row(telebot.types.InlineKeyboardButton('По названию ' + name_sign,
                                                callback_data=json.dumps(['srt', sort, 0]))) \
        .row(telebot.types.InlineKeyboardButton('По цене' + price_sign,
                                                callback_data=json.dumps(['srt', sort, 1])),
             telebot.types.InlineKeyboardButton('По наличию' + amount_sign,
                                                callback_data=json.dumps(['srt', sort, 2])))

    return sorting_markup


@bot.callback_query_handler(func=lambda call: json.loads(call.data)[0] == 'srt')
def show_sort_message_callback_handler(call: telebot.types.CallbackQuery):
    data = json.loads(call.data)
    sort: int = data[1]
    pressed: int = data[2]

    user = User(call.from_user.id)
    new_sort: int

    if sort in (pressed, pressed + 3, pressed - 3):
        new_sort = (sort + 3) if sort < 3 else (sort - 3)
    else:
        new_sort = pressed

    user.set_search({'sort': new_sort})
    try:
        # bot.edit_message_reply_markup(
        #     call.message.json['chat']['id'],
        #     call.message.id,
        #     call.inline_message_id,
        #     get_sort_message_markup(user)
        # )
        chat_id = call.message.json['chat']['id']
        bot.delete_message(chat_id, call.message.id)
        bot.delete_message(chat_id, call.message.id + 1)
        show_results(user.id, chat_id, user.get_search()['query'])

    except Exception as e:
        print('show_sort_message_callback_handler: ' + str(e))


def get_search_res_n_markup(user: User, query: str):

    sort: int = int(user.get_search()['sort'])
    order_by: str
    is_desk: bool
    if sort >= 3:
        is_desk = True
        sort -= 3
    else:
        is_desk = False
    if sort == 0:
        order_by = 'name'
    elif sort == 1:
        order_by = 'price'
    elif sort == 2:
        order_by = 'amount'

    row_count: int = int(user.get_settings()['on_page'])
    offset: int = int(user.get_search()['row'])

    res = gnrl_crud.find_products_by_category(str(query), order_by_field_name=order_by, is_desk=is_desk,
                                              row_count=row_count, offset=offset)
    if len(res) == 0:
        res = gnrl_crud.find_like_products_by_name(str(query), order_by_field_name=order_by, is_desk=is_desk,
                                                   row_count=row_count, offset=offset)

    if len(res) == 0:
        return [], None

    result_markup = telebot.types.InlineKeyboardMarkup()
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

        msg_txt = str(r.name) + str(' - ' if r.quantity is None else ', ' + str(r.quantity) + ' - ') + \
                  text_amount + ' - ' + str(r.price / 100) + 'Р'

        result_markup.row(telebot.types.InlineKeyboardButton(msg_txt, callback_data=json.dumps(['res', r.id])))

    res = gnrl_crud.find_products_by_category(str(query))
    if len(res) == 0:
        res = gnrl_crud.find_like_products_by_name(str(query))

    nav_buttons = [1 if offset != 0 else 0, 2 if len(res) - offset - row_count > 0 else 0]

    result_markup.add(telebot.types.InlineKeyboardButton('◀️' if nav_buttons[0] == 1 else '⏸',
                                                         callback_data=json.dumps(
                                                             ['nav', nav_buttons[0], query, user.id])),
                      telebot.types.InlineKeyboardButton('▶️' if nav_buttons[1] == 2 else '⏸',
                                                         callback_data=json.dumps(
                                                             ['nav', nav_buttons[1], query, user.id])))

    return res, result_markup


@bot.callback_query_handler(func=lambda call: json.loads(call.data)[0] == 'nav')
def navigation_callback_handler(call: telebot.types.CallbackQuery):
    data = json.loads(call.data)
    data1 = data[1]
    if data1 == 0:
        return

    query = data[2]
    user = User(data[3])
    offset = user.get_search()['row']
    on_page = user.get_settings()['on_page']

    if data1 == 1:
        offset -= on_page
        if offset < 0:
            offset = 0
    elif data1 == 2:
        offset += on_page
    user.set_search({'row': offset})

    print(str(user.get_search()))

    res, markup = get_search_res_n_markup(user, query)
    bot.edit_message_reply_markup(call.message.json['chat']['id'], call.message.id,
                                  call.inline_message_id, reply_markup=markup)


if __name__ == '__main__':
    if token is None:
        print('config file is not found')
    else:
        token = None
        print('bot is started')
        bot.polling()
