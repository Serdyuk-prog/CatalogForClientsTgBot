import telebot
import confing

bot = telebot.TeleBot(confing.TOKEN, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, "Hello, maaaaaaaaaaaaaaaan!, how're u, bra")


if __name__ == '__main__':
    print('bot is started')
    bot.polling()

