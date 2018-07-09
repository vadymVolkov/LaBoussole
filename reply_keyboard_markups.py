import time

import telebot
import commands


class Keyboard:
    def __init__(self, bot):
        self.bot = bot

    def select_lng(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Русский язык', 'Українська мова')
        self.bot.send_message(user_id, 'Добрый день, выберите пожалуйста язык бота.\n'
                                       'Добрий день, оберіть будь ласка мову бота.', reply_markup=user_markup)

    def main_menu_ru(self, message, user, admin):
        # get user id
        user_id = message.from_user.id
        user_full_name = ''
        if user[2]:
            user_full_name = ' ' + user[2]
        # get Basket
        basket = commands.make_basket(message)
        if not basket:
            basket = ''
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Купить журнал')
        user_markup.row('Подтвердить оплату')
        user_markup.row('Поменять язык')
        if basket:
            user_markup.row('Перейти к оформлению заказа')
            user_markup.row('Очистить корзину')
        if message.from_user.id == admin[0][1]:
            user_markup.row('/admin')
        self.bot.send_message(user_id, 'Добро пожаловать' + user_full_name + '!\n'
                              + basket +
                              'Что бы вы хотели сделать?', reply_markup=user_markup)

    def buy_journal_ru_step1(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        # get journals
        journals = commands.get_journals()
        for journal in journals:
            user_markup.row('vol: ' + str(journal[0]) + ' ' + str(journal[1]))
        # get basket
        basket = commands.make_basket(message)
        if basket:
            user_markup.row('Перейти к оформлению заказа')
            user_markup.row('Очистить корзину')
        if not basket:
            basket = ''
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, basket + 'Сейчас у нас в наличии есть следующие номера! \n'
                              + 'Какой из номеров вы бы хотели купить?', reply_markup=user_markup)

    def buy_journal_ru_step2(self, message):
        # get user id
        user_id = message.from_user.id
        journal = commands.check_selected_journal(message.text)
        store = journal[2]
        # if journal in store
        if store > 0:
            # set keyboard
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Да, хочу в праздничной упаковке')
            user_markup.row('Нет, хочу обычную упаковку')
            # add journal to order
            commands.add_order_to_basket(message, journal)
            self.bot.send_message(user_id, 'Супер, такой номер есть на нашем складе. '
                                           'Хочешь ли ты, чтобы мы его завернули в праздничную упаковку '
                                           '(это будет стоить +30 гривен)?',
                                  reply_markup=user_markup)
        # if journal not in store
        elif store == 0:
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Да, хочу заказать другой номер')
            # get basket
            basket = commands.make_basket(message)
            if basket:
                user_markup.row('Перейти к оформлению заказа')
            user_markup.row('Вернуться в главное меню')
            self.bot.send_message(user_id, 'К сожалению этот номер закончился.\n'
                                           'Хотите заказать другой номер?',
                                  reply_markup=user_markup)

    def buy_journal_ru_step2_extra_cover(self, message):
        # get user id
        user_id = message.from_user.id
        if message.text == 'Да, хочу в праздничной упаковке':
            commands.add_cover_to_basket(message)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Да, заказать еще один номер')
        user_markup.row('Перейти к оформлению заказа')
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, 'Хотите заказать еще один номер?', reply_markup=user_markup)

    def buy_journal_ru_step3(self, message):
        # get user id
        user_id = message.from_user.id
        # if user have order_data
        user_data = commands.get_user_data(message)
        if user_data:
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Да, оставить эти данные')
            user_markup.row('Нет, хочу их изменить')
            user_markup.row('Вернуться в главное меню')
            self.bot.send_message(user_id, 'Вы уже раньше оставляли свои данные:\n'
                                  + user_data +
                                  'Хотите их оставить?', reply_markup=user_markup)
        # if user is new
        else:
            user_markup = telebot.types.ReplyKeyboardRemove()
            msg = self.bot.send_message(user_id, 'Теперь мы можем приступить к оформлению заказа.\n' +
                                        'Напишите, пожалуйста, своё полное имя и фамилию',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_name)

    def buy_journal_ru_step4_name(self, message):
        # get user id
        user_id = message.from_user.id
        check_name = commands.check_entered_name(message.text)
        user_markup = telebot.types.ReplyKeyboardRemove()
        if check_name:
            commands.set_user_name(message, message.text)
            msg = self.bot.send_message(user_id,
                                        'Теперь напишите, пожалуйста, свой телефон в формате +380931234567',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_telephone)
        else:
            msg = self.bot.send_message(user_id,
                                        'Имя и фамилия указаны не верно, укажите их еще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_name)

    def buy_journal_ru_step4_telephone(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        check_telephone = commands.check_telephone(message.text)
        if check_telephone:
            commands.set_user_telephone(message, message.text)
            msg = self.bot.send_message(user_id,
                                        'Теперь напишите, пожалуйста, свой email в формате labusole@gmail.com',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_email)
        else:
            msg = self.bot.send_message(user_id,
                                        'Телефон указан не верно, укажите его еще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_telephone)

    def buy_journal_ru_step4_email(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        check_email = commands.check_email(message.text)
        if check_email:
            commands.set_user_email(message, message.text)
            msg = self.bot.send_message(user_id,
                                        'Теперь нам нужно узнать, куда доставлять журнал.\n'
                                        'Напишите, пожалуйста, свой Город и номер отделения Новой Почты. '
                                        'В формате “Одесса, 1”',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_adress)
        else:
            msg = self.bot.send_message(user_id,
                                        'Email указан не верно, укажите его еще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_email)

    def buy_journal_ru_step4_adress(self, message):
        # get user id
        user_id = message.from_user.id
        check_adress = commands.check_entered_adress(message.text)
        if check_adress:
            commands.set_user_adress(message, message.text)
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Подтвердить эти данные')
            user_markup.row('Указать данные заново')
            user_markup.row('Вернуться в главное меню')
            user_data = commands.get_user_data_unaccepted(message)
            self.bot.send_message(user_id,
                                  'Вы указали:\n' + user_data +
                                  'Подтвердить?\n',
                                  reply_markup=user_markup)
        else:
            user_markup = telebot.types.ReplyKeyboardRemove()
            msg = self.bot.send_message(user_id,
                                        'Адрес указан не верно, укажите его еще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ru_step4_adress)

    def buy_journal_ru_step5_comments(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        msg = self.bot.send_message(user_id, 'Укажите пожелание или коментарий к своеиму заказу',
                                    reply_markup=user_markup)
        self.bot.register_next_step_handler(msg, self.buy_journal_ru_step6_payment)

    def buy_journal_ru_step6_payment(self, message):
        # get user id
        user_id = message.from_user.id
        commands.add_comment_to_basket(message, message.text)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Банковская карта')
        user_markup.row('Наложенный платёж')
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, 'Выбери удобный для себя способ оплаты:', reply_markup=user_markup)

    def buy_journal_ru_step7_card(self, message):
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.add_payment_to_basket(message, message.text)
        card_number = 'XXXX XXXX XXXX XXXX'
        price = str(basket[2])
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Да, дата доставки подходит')
        user_markup.row('Нет, указать дату доставки')
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, 'Спасибо за заказ!\n'
                              + 'Полная сумма твоего заказа = ' + price + ' гривен.\n'
                              + 'Чтобы мы могли как можно скорее отправить твой журнал,'
                                ' оплати его по следующим реквизитам - ' + card_number + '.\n'
                              + 'После этого нам понадобится время, чтобы обработать'
                                ' твой платёж (в среднем до 1 дня).'
                                '\nПроцесс будет быстрее, если ты пришлёшь скриншот или фотографию квитанции '
                                'выбрав в главном меню пункт \'Подтвердить оплату\'.\n'
                              + 'Ваш заказ будет доставлен ориентировочно в течение 1-2 рабочих дней.\n'
                              + 'Удобно ли вам будет в это время его получить?',
                              reply_markup=user_markup)

    def buy_journal_ru_step7_onrecieve(self, message):
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.add_payment_to_basket(message, message.text)
        price = str(basket[2])
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Да, дата доставки подходит')
        user_markup.row('Нет, указать дату доставки')
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, 'Спасибо за заказ!\n'
                              + 'Полная сумма твоего заказа = ' + price + ' гривен.\n'
                              + 'Ваш заказ будет доставлен ориентировочно в течение 1-2 рабочих дней.\n'
                              + 'Удобно ли вам будет в это время его получить?', reply_markup=user_markup)

    def buy_journal_ru_step8_receive_date(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        msg = self.bot.send_message(user_id, 'Укажите желаемое число доставки в формате 31.07.2018',
                                    reply_markup=user_markup)
        self.bot.register_next_step_handler(msg, self.buy_journal_ru_finish_another_date)

    def buy_journal_ru_finish(self, message, user, admin):
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.accept_basket(message)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, 'Ваш заказ  подтвержден. \nСкоро с вами свяжеться наш менеджер.',
                              reply_markup=user_markup)
        self.bot.send_message(admin[0][1],
                              'Получен новый заказ от пользователя с ID ' + str(user[1]) + '. Номер заказа ' + str(
                                  basket[6]))

    def buy_journal_ru_finish_another_date(self, message):
        # get admin
        admin = commands.get_admins(1)
        # get User
        user = commands.get_user(message)
        # set delivery date to basket
        commands.add_delivery_date_to_basket(message, message.text)
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.accept_basket(message)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Вернуться в главное меню')
        self.bot.send_message(user_id, 'Ваш заказ  подтвержден. \nСкоро с вами свяжеться наш менеджер.',
                              reply_markup=user_markup)
        self.bot.send_message(admin[0][1],
                              'Получен новый заказ от пользователя с ID ' + str(user[1]) + '. Номер заказа ' + str(
                                  basket[6]))

    def process_accept_payment_ru(self, message):
        # get user id
        user_id = message.from_user.id
        hide_markup = telebot.types.ReplyKeyboardRemove()
        msg = self.bot.send_message(user_id, "Отлично, можете отправить фото квитанции об оплате",
                                    reply_markup=hide_markup)
        self.bot.register_next_step_handler(msg, self.process_ru_photo_receive)

    def process_ru_photo_receive(self, message):
        # get admin
        admin = commands.get_admins(1)
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Вернуться в главное меню')
        photo_id = message.photo[2].file_id
        self.bot.send_photo(admin[0][1], photo_id)
        self.bot.send_message(admin[0][1],
                              'Пользователь с ID ' + str(user_id) + ' прислал вам фотографию квитанции об оплате',
                              reply_markup=user_markup)
        self.bot.send_message(user_id, 'Отлично, ваша квитанция была отрпалена нашему менджеру.\n'
                                       'Ожидайте номера накладной', reply_markup=user_markup)

    def main_menu_ua(self, message, user, admin):
        # get user id
        user_id = message.from_user.id
        user_full_name = ''
        if user[2]:
            user_full_name = ' ' + user[2]
        # get Basket
        basket = commands.make_basket(message)
        if not basket:
            basket = ''
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Придбати журнал')
        user_markup.row('Підтвердити оплату')
        user_markup.row('Змінити мову')
        if basket:
            user_markup.row('Перейти до замовлення')
            user_markup.row('Очистити кошик')
        if message.from_user.id == admin[0][1]:
            user_markup.row('/admin')
        self.bot.send_message(user_id, 'Ласкаво просимо' + user_full_name + '!\n'
                              + basket +
                              'Що б ви хотіли зробити?', reply_markup=user_markup)

    def buy_journal_ua_step1(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        # get journals
        journals = commands.get_journals_from_docks()
        for journal in journals:
            user_markup.row('vol: ' + str(journal[0]) + ' ' + str(journal[1]))
        # get basketsl
        basket = commands.make_basket(message)
        if basket:
            user_markup.row('Перейти до оформлення замовлення')
            user_markup.row('Очистити кошик')
        if not basket:
            basket = ''
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, basket + 'Зараз у нас в наявності є наступні номери! \n'
                              + 'Який з номерів ви б хотіли купити?', reply_markup=user_markup)

    def buy_journal_ua_step2(self, message):
        # get user id
        user_id = message.from_user.id
        journal = commands.check_selected_journal(message.text)
        store = journal[2]
        # if journal in store
        if store > 0:
            # set keyboard
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Так, хочу в святковій обкладинці')
            user_markup.row('Ні, хочу звичайну обкладинку')
            # add journal to order
            commands.add_order_to_basket(message, journal)
            self.bot.send_message(user_id, 'Супер, такий номер є на нашому складі. '
                                           'Чи хочеш ти, щоб ми його загорнули у святкову обкладинку '
                                           '(це буде коштувати +30 гривень)?',
                                  reply_markup=user_markup)
        # if journal not in store
        elif store == 0:
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Так, хочу замовити інший номер')
            # get basket
            basket = commands.make_basket(message)
            if basket:
                user_markup.row('Перейти до оформлення замовлення')
            user_markup.row('Повернутися в головне меню')
            self.bot.send_message(user_id, 'На жаль цей номер закінчився.\n'
                                           'Хочете замовити інший номер?',
                                  reply_markup=user_markup)

    def buy_journal_ua_step2_extra_cover(self, message):
        # get user id
        user_id = message.from_user.id
        if message.text == 'Так, хочу в святковій обкладинці':
            commands.add_cover_to_basket(message)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Так, замовити ще один номер')
        user_markup.row('Перейти до оформлення замовлення')
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, 'Хочете замовити ще один номер?', reply_markup=user_markup)

    def buy_journal_ua_step3(self, message):
        # get user id
        user_id = message.from_user.id
        # if user have order_data
        user_data = commands.get_user_data(message)
        if user_data:
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Так, залишити ці дані')
            user_markup.row('Ні, хочу їх змінити')
            user_markup.row('Повернутися в головне меню')
            self.bot.send_message(user_id, 'Ви вже раніше залишали свої дані:\n'
                                  + user_data +
                                  'Хочете їх залишити?', reply_markup=user_markup)
        # if user is new
        else:
            user_markup = telebot.types.ReplyKeyboardRemove()
            msg = self.bot.send_message(user_id, 'Зараз ми можемо розпочати  оформлення замовлення.\n' +
                                        'Напиши, будь ласка, своє повне ім\'я та прізвище',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_name)

    def buy_journal_ua_step4_name(self, message):
        # get user id
        user_id = message.from_user.id
        check_name = commands.check_entered_name(message.text)
        user_markup = telebot.types.ReplyKeyboardRemove()
        if check_name:
            commands.set_user_name(message, message.text)
            msg = self.bot.send_message(user_id,
                                        'Зараз напиши, будь ласка, свій телефон в форматі +380931234567',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_telephone)
        else:
            msg = self.bot.send_message(user_id,
                                        'Неправильно вказані ім\'я та прізвище, вкажіть їх ще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_name)

    def buy_journal_ua_step4_telephone(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        check_telephone = commands.check_telephone(message.text)
        if check_telephone:
            commands.set_user_telephone(message, message.text)
            msg = self.bot.send_message(user_id,
                                        'Зараз напиши, будь ласка, свій email у форматі labusole@gmail.com',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_email)
        else:
            msg = self.bot.send_message(user_id,
                                        'Неправильно вказано номер телефону, вкажіть його ще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_telephone)

    def buy_journal_ua_step4_email(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        check_email = commands.check_email(message.text)
        if check_email:
            commands.set_user_email(message, message.text)
            msg = self.bot.send_message(user_id,
                                        'Зараз нам потрібно дізнатися, куди доставити журнал.\n'
                                        'Напиши, будь ласка, свое місто і номер відділення Нової Пошти. '
                                        'У форматі "Одеса, 1”.',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_adress)
        else:
            msg = self.bot.send_message(user_id,
                                        'Неправильно вказано email, вкажіть його ще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_email)

    def buy_journal_ua_step4_adress(self, message):
        # get user id
        user_id = message.from_user.id
        check_adress = commands.check_entered_adress(message.text)
        if check_adress:
            commands.set_user_adress(message, message.text)
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('Підтвердити ці дані')
            user_markup.row('Вказати дані заново')
            user_markup.row('Повернутися в головне меню')
            user_data = commands.get_user_data_unaccepted(message)
            self.bot.send_message(user_id,
                                  'Ви вказали:\n' + user_data +
                                  'Підтвердити?\n',
                                  reply_markup=user_markup)
        else:
            user_markup = telebot.types.ReplyKeyboardRemove()
            msg = self.bot.send_message(user_id,
                                        'Неправильно вказано адресу, вкажіть її ще раз',
                                        reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.buy_journal_ua_step4_adress)

    def buy_journal_ua_step5_comments(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        msg = self.bot.send_message(user_id, 'Вкажіть побажання або коментар до свого замовлення',
                                    reply_markup=user_markup)
        self.bot.register_next_step_handler(msg, self.buy_journal_ua_step6_payment)

    def buy_journal_ua_step6_payment(self, message):
        # get user id
        user_id = message.from_user.id
        commands.add_comment_to_basket(message, message.text)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Банківська картка')
        user_markup.row('Накладений платіж')
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, 'Вибери зручний для себе спосіб оплати::', reply_markup=user_markup)

    def buy_journal_ua_step7_card(self, message):
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.add_payment_to_basket(message, message.text)
        card_number = 'XXXX XXXX XXXX XXXX'
        price = str(basket[2])
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Так, дата доставки підходить')
        user_markup.row('Ні, вказати дату доставки')
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, 'Спасибі за замовлення!\n'
                              + 'Повна сума твого замовлення = ' + price + ' гривен.\n'
                              + 'Щоб ми могли якомога швидше відправити твій журнал,'
                                ' оплати його за наступними реквізитами - ' + card_number + '.\n'
                              + 'Після цього нам знадобиться час, щоб обробити твій платіж (в середньому до 1 дня).'
                                '\nПроцес буде швидше, якщо ти відправиш скріншот або фотографію квитанції '
                                'вибравши в головному меню пункт \'Підтвердити оплату\'\n.'
                              + 'Ваше замовлення буде доставлено орієнтовно протягом 1-2 робочих днів.\n'
                              + 'Чи зручно вам буде в цей час його отримати?',
                              reply_markup=user_markup)

    def buy_journal_ua_step7_onrecieve(self, message):
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.add_payment_to_basket(message, message.text)
        price = str(basket[2])
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Так, дата доставки підходить')
        user_markup.row('Ні, вказати дату доставки')
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, 'Спасибі за замовлення!\n'
                              + 'Повна сума твого замовлення = ' + price + ' гривен.\n'
                              + 'Ваше замовлення буде доставлено орієнтовно протягом 1-2 робочих днів.\n'
                              + 'Чи зручно вам буде в цей час його отримати?', reply_markup=user_markup)

    def buy_journal_ua_step8_receive_date(self, message):
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardRemove()
        msg = self.bot.send_message(user_id, 'Вкажіть бажану дату доставки в форматі 31.07.2018',
                                    reply_markup=user_markup)
        self.bot.register_next_step_handler(msg, self.buy_journal_ua_finish_another_date)

    def buy_journal_ua_finish(self, message, user, admin):
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.accept_basket(message)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, 'Ваше замовлення підтверджено. \nСкоро з вами зв\'яжется наш менеджер.',
                              reply_markup=user_markup)
        self.bot.send_message(admin[0][1],
                              'Получен новый заказ от пользователя с ID ' + str(user[1]) + '. Номер заказа ' + str(
                                  basket[6]))

    def buy_journal_ua_finish_another_date(self, message):
        # get admin
        admin = commands.get_admins(1)
        # get User
        user = commands.get_user(message)
        # set delivery date to basket
        commands.add_delivery_date_to_basket(message, message.text)
        # get user id
        user_id = message.from_user.id
        # get basket
        basket = commands.get_basket(message)
        commands.accept_basket(message)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Повернутися в головне меню')
        self.bot.send_message(user_id, 'Ваше замовлення підтверджено. \nСкоро з вами зв\'яжется наш менеджер.',
                              reply_markup=user_markup)
        self.bot.send_message(admin[0][1],
                              'Получен новый заказ от пользователя с ID ' + str(user[1]) + '. Номер заказа ' + str(
                                  basket[6]))

    def process_accept_payment_ua(self, message):
        # get user id
        user_id = message.from_user.id
        hide_markup = telebot.types.ReplyKeyboardRemove()
        msg = self.bot.send_message(user_id, "Відмінно, можете відправити фото квитанції про сплату",
                                    reply_markup=hide_markup)
        self.bot.register_next_step_handler(msg, self.process_ua_photo_receive)

    def process_ua_photo_receive(self, message):
        # get admin
        admin = commands.get_admins(1)
        # get user id
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Повернутися в головне меню')
        photo_id = message.photo[2].file_id
        self.bot.send_photo(admin[0][1], photo_id)
        self.bot.send_message(admin[0][1],
                              'Пользователь с ID ' + str(user_id) + ' прислал вам фотографию квитанции об оплате',
                              reply_markup=user_markup)
        self.bot.send_message(user_id, 'Відмінно, ваша квитанція була отрпалена нашому менджер.\n'
                                       'Чекайте номера накладної', reply_markup=user_markup)

    def admin_commands(self, message, admin):
        user_id = message.from_user.id
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('Обновить базу данных журналов')
        user_markup.row('Обновить базу данных оповещений')
        user_markup.row('Разослать оповещения')
        user_markup.row('Отправить всем пользователям сообщение')
        user_markup.row('Отправить всем пользователям сообщение с интервалом в 1 минуту')
        user_markup.row('/start')
        if user_id == admin[0][1]:
            msg = self.bot.send_message(user_id, 'Привет админ \n'
                                                 'Выбери команду:', reply_markup=user_markup)
            self.bot.register_next_step_handler(msg, self.admin_command_send)

    def admin_command_send(self, message):
        # get admin
        admins = commands.get_admins(1)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row('/admin')
        user_markup.row('/start')
        user_id = message.from_user.id
        if user_id == admins[0][1]:
            if message.text == 'Обновить базу данных журналов':
                try:
                    commands.update_journal_db()
                    self.bot.send_message(user_id, "База успешно обновлена", reply_markup=user_markup)
                except:
                    self.bot.send_message(user_id, "Упс, произошла ошибка.", reply_markup=user_markup)
            elif message.text == 'Обновить базу данных оповещений':
                try:
                    commands.update_orders()
                    self.bot.send_message(user_id, "База успешно обновлена", reply_markup=user_markup)
                except:
                    self.bot.send_message(user_id, "Упс, произошла ошибка.", reply_markup=user_markup)
            elif message.text == 'Разослать оповещения':
                try:
                    notification_count = commands.send_notification(self.bot)
                    self.bot.send_message(user_id, "Отправленно " + str(notification_count) + ' оповещений',
                                          reply_markup=user_markup)
                except:
                    self.bot.send_message(user_id, "Упс, произошла ошибка.", reply_markup=user_markup)
            elif message.text == 'Отправить всем пользователям сообщение':
                msg = self.bot.send_message(user_id,
                                            'Напишите пожалуйста сообщение которое'
                                            ' вы хотите отправить всем пользователям',
                                            reply_markup=user_markup)
                self.bot.register_next_step_handler(msg, self.send_message_all_users)
            elif message.text == 'Отправить всем пользователям сообщение с интервалом в 1 минуту':
                msg = self.bot.send_message(user_id,
                                            'Напишите пожалуйста сообщение которое'
                                            ' вы хотите отправить всем пользователям с интервалом в 1 минуту',
                                            reply_markup=user_markup)
                self.bot.register_next_step_handler(msg, self.send_message_all_users)


    def send_message_all_users(self, message):
        text = message.text
        users = commands.get_all_users_id()
        for user in users:
            self.bot.send_message(user[1], text)

    def send_message_all_users_1_min_interval(self, message):
        users = commands.get_all_users_id()
        text = message.text
        for user in users:
            self.bot.send_message(user[1], text)
            time.sleep(60)
