#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with CherryPy
# It echoes any incoming text messages and does not use the polling method.
import time

from config import config
import commands
import cherrypy
import telebot
from reply_keyboard_markups import Keyboard

API_TOKEN = config.token

WEBHOOK_HOST = config.ip
WEBHOOK_PORT = config.port  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = config.listen  # In some VPS you may need to put here the IP addr

#WEBHOOK_SSL_CERT = './ssl_cert/webhook_cert.pem'  # Path to the ssl certificate
#WEBHOOK_SSL_PRIV = './ssl_cert/webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_SSL_CERT = '/root/LaBoussole/ssl_cert/webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = '/root/LaBoussole/ssl_cert/webhook_pkey.pem'  # Path to the ssl private key
# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

bot = telebot.TeleBot(API_TOKEN)
keyboard = Keyboard(bot)


# WebhookServer, process webhook calls
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(commands=['start'])
def handle_text(message):
    # get admin
    admin = commands.check_user_id_for_admin_rights(message)
    # get User
    user = commands.get_user(message)
    if user:
        user_lng = user[6]
    else:
        user_lng = 0
    # if lng not selected
    if user_lng == 0:
        keyboard.select_lng(message)
    # if lng ru
    elif user_lng == 1:
        keyboard.main_menu_ru(message, user, admin)
    # if lng ua
    elif user_lng == 2:
        keyboard.main_menu_ua(message, user, admin)


@bot.message_handler(commands=['admin'])
def handle_text(message):
    # get admin
    admin = commands.check_user_id_for_admin_rights(message)
    if message.from_user.id == admin[1]:
        keyboard.admin_commands(message, admin)


@bot.message_handler(
    func=lambda mess: "Вернуться в главное меню" == mess.text or "Повернутися в головне меню" == mess.text,
    content_types=['text'])
def handle_text(message):
    # get admin
    admin = commands.check_user_id_for_admin_rights(message)
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    # if lng not selected
    if user_lng == 0:
        keyboard.select_lng(message)
    # if lng ru
    elif user_lng == 1:
        keyboard.main_menu_ru(message, user, admin)
    # if lng ua
    elif user_lng == 2:
        keyboard.main_menu_ua(message, user, admin)


@bot.message_handler(func=lambda mess: "Русский язык" == mess.text or "Українська мова" == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get admin
    admin = commands.check_user_id_for_admin_rights(message)
    lng = message.text
    if lng == 'Русский язык':
        commands.set_user_lng(message, 1)
        # get User
        user = commands.get_user(message)
        keyboard.main_menu_ru(message, user, admin)
    elif lng == 'Українська мова':
        commands.set_user_lng(message, 2)
        # get User
        user = commands.get_user(message)
        keyboard.main_menu_ua(message, user, admin)


@bot.message_handler(func=lambda mess: "Купить журнал" == mess.text or "Придбати журнал" == mess.text
                                       or 'Да, хочу заказать другой номер' == mess.text
                                       or 'Так, хочу замовити інший номер' == mess.text
                                       or 'Да, заказать еще один номер' == mess.text
                                       or 'Так, замовити ще один номер' == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step1(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step1(message)


@bot.message_handler(func=lambda mess: "Подтвердить оплату" == mess.text or "Підтвердити оплату" == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.process_accept_payment_ru(message)
    elif user_lng == 2:
        keyboard.process_accept_payment_ua(message)


@bot.message_handler(func=lambda mess: "Поменять язык" == mess.text or "Змінити мову" == mess.text,
                     content_types=['text'])
def handle_text(message):
    commands.set_user_lng(message, 0)
    keyboard.select_lng(message)


@bot.message_handler(func=lambda mess: "Очистить корзину" == mess.text or "Очистити кошик" == mess.text,
                     content_types=['text'])
def handle_text(message):
    commands.clean_basket(message)
    # get admin
    admin = commands.check_user_id_for_admin_rights(message)
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    # if lng ru
    if user_lng == 1:
        keyboard.main_menu_ru(message, user, admin)
    # if lng ua
    elif user_lng == 2:
        keyboard.main_menu_ua(message, user, admin)


@bot.message_handler(func=lambda mess: commands.check_command(mess.text, commands.get_journals_names_from_db()),
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step2(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step2(message)


@bot.message_handler(func=lambda mess: "Да, хочу в подарочной упаковке" == mess.text
                                       or "Нет, хочу обычную упаковку" == mess.text
                                       or "Так, хочу в подарунковій упаковці" == mess.text
                                       or "Ні, хочу звичайну упаковку" == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step2_extra_cover(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step2_extra_cover(message)


@bot.message_handler(func=lambda mess: "Перейти к оформлению заказа" == mess.text
                                       or "Перейти до оформлення замовлення" == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step3(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step3(message)


@bot.message_handler(func=lambda mess: "Нет, хочу их изменить" == mess.text or 'Указать данные заново' == mess.text
                                       or "Ні, хочу їх змінити" == mess.text or 'Вказати дані заново' == mess.text,
                     content_types=['text'])
def handle_text(message):
    commands.unaccept_user_data(message)
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step3(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step3(message)


@bot.message_handler(func=lambda mess: "Подтвердить эти данные" == mess.text or 'Да, оставить эти данные' == mess.text
                                       or "Підтвердити ці дані" == mess.text or 'Так, залишити ці дані' == mess.text,
                     content_types=['text'])
def handle_text(message):
    commands.accept_user_data(message)
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step5_comments(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step5_comments(message)


@bot.message_handler(func=lambda mess: "Банковская карта" == mess.text or 'Банківська картка' == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step7_card(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step7_card(message)


@bot.message_handler(func=lambda mess: "Наложенный платёж" == mess.text or 'Післяплата' == mess.text,
                     content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step7_onrecieve(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step7_onrecieve(message)


@bot.message_handler(
    func=lambda mess: "Да, дата доставки подходит" == mess.text or 'Так, дата доставки підходить' == mess.text,
    content_types=['text'])
def handle_text(message):
    # get admin
    admin = commands.get_admins(1)
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_finish(message, user, admin)
    elif user_lng == 2:
        keyboard.buy_journal_ua_finish(message, user, admin)


@bot.message_handler(
    func=lambda mess: "Нет, указать дату доставки" == mess.text or 'Ні, вказати дату доставки' == mess.text,
    content_types=['text'])
def handle_text(message):
    # get User
    user = commands.get_user(message)
    user_lng = user[6]
    if user_lng == 1:
        keyboard.buy_journal_ru_step8_receive_date(message)
    elif user_lng == 2:
        keyboard.buy_journal_ua_step8_receive_date(message)


# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Disable CherryPy requests log
access_log = cherrypy.log.access_log
for handler in tuple(access_log.handlers):
    access_log.removeHandler(handler)

# Start cherrypy server
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

