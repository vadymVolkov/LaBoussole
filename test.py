import telebot

bot = telebot.TeleBot("552719481:AAE0Uk5GKQoNcCmbTI3UVFYrqMOYj8Cld6o")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


bot.polling()