import db
from collections import Counter
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from config import config
import xlsxwriter

ORDER_KEY = config.order_key


def get_user(message):
    user_id = message.from_user.id
    user = db.get_user_byid(user_id)
    if not user:
        add_user(message)
    return user


def get_admins(rights):
    admins = db.get_admins(rights)
    return admins


def add_user(message):
    user_id = message.from_user.id
    user_telegram = message.from_user.username
    db.add_new_user(user_id, user_telegram)


def set_user_lng(message, lng):
    user_id = message.from_user.id
    db.set_user_lng(user_id, lng)


def get_journals():
    journals = db.get_journals()
    return journals


def check_selected_journal(journal):
    journal = journal.split(' ')
    try:
        name = journal[2]
    except IndexError:
        return None
    result = db.get_journal_by_name(name)
    return result


def add_order_to_basket(message, journal):
    user_id = message.from_user.id
    basket = db.get_basket_by_userid(user_id)
    order = 'vol: ' + str(journal[0]) + ' ' + str(journal[1]) + '; '
    journal_price = 300
    if basket:
        basket_order = basket[1]
        basket_order = basket_order + order
        basket_price = basket[2]
        basket_price = basket_price + journal_price
        db.add_order_to_basket(user_id, basket_order)
        db.add_price_to_basket(user_id, basket_price)

    elif not basket:
        db.add_new_order_to_basket(user_id, order)


def add_cover_to_basket(message):
    user_id = message.from_user.id
    user = db.get_user_byid(user_id)
    cover_price = 30
    if user[6] == 1:
        cover = 'в подарочной упаковке; '
    elif user[6] == 2:
        cover = 'в святковій обкладинці; '
    # db.add_cover_to_basket(user_id)
    basket = db.get_basket_by_userid(user_id)
    basket_order = basket[1]
    basket_order = basket_order[0:-2]
    basket_order = basket_order + ' ' + cover
    db.add_order_to_basket(user_id, basket_order)
    basket_price = basket[2]
    basket_price = basket_price + cover_price
    db.add_price_to_basket(user_id, basket_price)


def add_payment_to_basket(message, payment):
    user_id = message.from_user.id
    db.add_paymenbt_type_to_basket(user_id, payment)


def add_comment_to_basket(message, comment):
    user_id = message.from_user.id
    db.add_comment_to_basket(user_id, comment)


def add_delivery_date_to_basket(message, date):
    user_id = message.from_user.id
    db.add_delivery_date_to_basket(user_id, date)


def accept_basket(message):
    user_id = message.from_user.id
    make_basket_record(user_id)
    db.set_basket_achieve_true(user_id)


def get_list_of_order(message):
    user_id = message.from_user.id
    try:
        basket = db.get_basket_by_userid(user_id)
        orders = basket[1]
        orders = orders.split(';')
        orders = orders[0:-1]
        return orders
    except TypeError:
        return None


def get_basket(message):
    user_id = message.from_user.id
    try:
        basket = db.get_basket_by_userid(user_id)
        return basket
    except TypeError:
        return None


def cancel_last_order(message):
    user_id = message.from_user.id
    orders = get_list_of_order(message)
    if not orders:
        return
    orders = orders[0:-1]
    result = ''
    for order in orders:
        result = result + order + ';'
    result = result + ' '
    db.add_order_to_basket(user_id, result)


def clean_basket(message):
    user_id = message.from_user.id
    db.set_basket_achieve_true(user_id)


def make_basket(message):
    user_id = message.from_user.id
    user = db.get_user_byid(user_id)
    lng = user[6]
    orders = calculate_order(user_id)
    if orders:
        if lng == 1:
            result = 'У вас в корзине: \n'
        elif lng == 2:
            result = 'У вашому кошику: \n'
        for order in orders:
            result = result + order + ' шт.' '\n'
        return result
    if not orders:
        return None


def calculate_order(user_id):
    try:
        basket = db.get_basket_by_userid(user_id)
        orders = basket[1]
        orders = orders.split('; ')
        orders = orders[0:-1]
        count = Counter(orders)
        lists_of_count = list(count)
        result = []
        for element in lists_of_count:
            result.append(str(element) + ' x ' + str(count[element]))
        return result
    except TypeError:
        return None


def get_user_data(message):
    user_id = message.from_user.id
    user_data = db.get_user_data_by_userid(user_id)
    user = db.get_user_byid(user_id)
    lng = user[6]
    if user_data:
        if lng == 1:
            result = 'Полное имя: ' + user_data[0] + '\n' + \
                     'Номер телефона: ' + user_data[1] + '\n' + \
                     'Email: ' + user_data[2] + '\n' + \
                     'Адрес доставки: ' + user_data[3] + '\n'
            return result
        elif lng == 2:
            result = 'Повне ім\'я:' + user_data[0] + '\n' + \
                     'Номер телефону: ' + user_data[1] + '\n' + \
                     'Email: ' + user_data[2] + '\n' + \
                     'Адреса доставки: ' + user_data[3] + '\n'
            return result
    else:
        return None


def unaccept_user_data(message):
    user_id = message.from_user.id
    db.unaccept_user_data(user_id)


def set_user_name(message, name):
    user_id = message.from_user.id
    db.set_user_data_full_name(user_id, name)


def set_user_telephone(message, telephone):
    user_id = message.from_user.id
    db.set_user_data_telephone(user_id, telephone)


def set_user_email(message, email):
    user_id = message.from_user.id
    db.set_user_data_email(user_id, email)


def set_user_adress(message, adress):
    user_id = message.from_user.id
    db.set_user_data_adress(user_id, adress)


def accept_user_data(message):
    user_id = message.from_user.id
    db.accept_user_data(user_id)


def check_entered_name(name):
    result = name.split(' ')
    if len(result) < 2:
        return False
    else:
        return True


def check_entered_adress(adress):
    result = adress.split(' ')
    if len(result) < 2 or len(result) > 2:
        return False
    else:
        return True


def check_telephone(telephone):
    result = re.match(r'[+]{1}[0-9]{12}', telephone)
    if result and len(telephone) == 13:
        return True
    else:
        return False


def check_email(email):
    result = re.fullmatch('(^|\s)[-a-zA-Z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)', email)

    if result:
        return True
    else:
        return False


def get_user_data_unaccepted(message):
    user_id = message.from_user.id
    user_data = db.get_user_data_by_userid_unaccepted(user_id)
    user = db.get_user_byid(user_id)
    lng = user[6]
    if user_data:
        if lng == 1:
            result = 'Полное имя: ' + user_data[0] + '\n' + \
                     'Номер телефона: ' + user_data[1] + '\n' + \
                     'Email: ' + user_data[2] + '\n' + \
                     'Адрес доставки: ' + user_data[3] + '\n'
            return result
        elif lng == 2:
            result = 'Повне ім\'я:' + user_data[0] + '\n' + \
                     'Номер телефону: ' + user_data[1] + '\n' + \
                     'Email: ' + user_data[2] + '\n' + \
                     'Адреса доставки: ' + user_data[3] + '\n'
            return result
    else:
        return None


def make_basket_record(user_id):
    # get user
    user = db.get_user_byid(user_id)
    # get basket
    basket = db.get_basket_by_userid(user_id)
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('config/client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by key and open the first sheet
    sheet = client.open_by_key(ORDER_KEY).sheet1
    now = datetime.datetime.now()
    date = str(now.date()) + '.' + str(now.month) + '.' + str(now.year) + ' ' + str(now.hour) + ':' + str(now.minute)
    user_name = user[2]
    telegram_username = user[7]
    user_telephone = user[3]
    order_number = basket[6]
    order_list = calculate_order(user_id)
    order_list_final = ''
    for a in order_list:
        order_list_final = order_list_final + a + 'шт., '
    comments = basket[3]
    payment_metode = basket[5]
    delivery_adress = user[5]
    delivery_date = basket[4]
    total_price = basket[2]
    data = [date, user_id, user_name, telegram_username, user_telephone, order_number, order_list_final, comments,
            payment_metode, delivery_adress, delivery_date, total_price]
    sheet.append_row(data)


def get_journals_from_docks():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('config/client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by key and open the first sheet
    sheet = client.open_by_key(ORDER_KEY).get_worksheet(1)
    result = sheet.get_all_values()
    result = result[1:]
    return result


def create_feedback(user_id, feedback):
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('config/client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by key and open the first sheet
    sheet = client.open_by_key(ORDER_KEY).get_worksheet(2)
    data = [user_id, feedback]
    sheet.append_row(data)


def update_journal_db():
    journal_list = get_journals_from_docks()
    for journal in journal_list:
        vol = journal[0]
        name = journal[1]
        store = journal[2]
        journal_in_db = db.get_journal_by_name(name)
        if journal_in_db:
            db.update_journal_by_name(name, store)
        else:
            db.add_new_journal(vol, name, store)


def get_orders_from_google():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('config/client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by key and open the first sheet
    sheet = client.open_by_key(ORDER_KEY).get_worksheet(0)
    result = sheet.get_all_values()
    result = result[1:]
    return result


def update_orders():
    orders = get_orders_from_google()
    for order in orders:
        user_id = order[1]
        order_number = order[5]
        if order[12]:
            order_delivery_number = order[12]
        else:
            order_delivery_number = 'empty'
        notification = db.get_notification_by_order_number(order_number)
        if notification:
            if order[12]:
                db.set_delivery_number_in_notification(order_number, order_delivery_number)
        elif not notification:
            if order[12]:
                db.add_new_delivery_notification(order_number, user_id, order_delivery_number)


def send_notification(bot):
    notification_not_send = db.get_not_send_notifications()
    notification_count = 0
    for notification in notification_not_send:
        delivery_number = str(notification[3])
        order_number = str(notification[1])
        notify = notification[4]
        user_id = str(notification[2])
        user = db.get_user_byid(user_id)

        if not notify:

            if user[6] == 1:
                db.set_notifications_sended(delivery_number)
                bot.send_message(user_id, "Ваш заказ отправлен.\n"
                                          "Номер вашего заказа: " + order_number + '\n'
                                                                                   "Номер вашей накладной: "
                                 + delivery_number)
            elif user[6] == 2:
                db.set_notifications_sended(delivery_number)
                bot.send_message(user_id, "Ваше замовлення відправлено.\n"
                                          "Номер вашого замовлення " + order_number + "\n"
                                                                                      "Номер вашої накладної: "
                                 + delivery_number)
            notification_count = notification_count + 1
    return notification_count


def get_all_users_id():
    users_id = db.get_users_id()
    return users_id


def check_command(command, list_of_commands):
    for com in list_of_commands:
        if command == com:
            return True
    return False


def get_journals_names_from_db():
    journal_list = []
    journals = db.get_journals()
    for journal in journals:
        name = 'vol: ' + str(journal[0]) + ' ' + journal[1]
        journal_list.append(name)
    return journal_list


def check_user_id_for_admin_rights(message):
    user_id = message.from_user.id
    admins = get_admins(1)
    for admin in admins:
        if str(admin[1]) == str(user_id):
            return admin
    return "not admin"


def clean_comment(comment):
    reg = re.compile('[^a-zA-Z ]')
    result = reg.sub('', comment)
    return result


def create_report(name, data):
    workbook = xlsxwriter.Workbook(str(name) + '.xlsx')
    worksheet = workbook.add_worksheet()
    row = 1
    for d in data:
        col = 0
        for p in d:
            worksheet.write(row, col, p)
            col += 1
        row += 1
    workbook.close()

def create_all_reports():
    orders = db.get_all_orders_from_basket()
    create_report('orders', orders)
    users = db.get_all_users()
    create_report('users', users)