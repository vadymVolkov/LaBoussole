import mysql.connector
import mysql
from config import config
import commands


def connection():
    conn = mysql.connector.connect(
        host=config.host,
        user=config.user,
        passwd=config.password,
        database=config.db,
        use_unicode=True,
        charset="utf8")

    return conn


def get_user_byid(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = "select * from users where user_id = %s"
    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def add_new_user(user_id, user_telegram):
    conn = connection()
    cursor = conn.cursor()
    sql = "insert into users  (user_id, user_telegram) values (%s, %s)"
    cursor.execute(sql, (user_id, user_telegram,))
    conn.commit()
    conn.close()


def set_user_lng(user_id, lng):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set  user_lng = %s where user_id = %s"
    cursor.execute(sql, (lng, user_id,))
    conn.commit()
    conn.close()


def get_journals():
    conn = connection()
    cursor = conn.cursor()
    sql = "select vol, name, store from journals"
    cursor.execute(sql)
    journals = cursor.fetchall()
    conn.close()
    return journals


def get_journal_by_name(name):
    conn = connection()
    cursor = conn.cursor()
    sql = "select vol, name, store from journals where name = %s"
    cursor.execute(sql, (name,))
    journal = cursor.fetchone()
    conn.close()
    return journal


def add_new_journal(vol, name, store):
    conn = connection()
    cursor = conn.cursor()
    sql = "insert into journals (vol, name, store) VALUES (%s, %s, %s)"
    cursor.execute(sql, (vol, name, store,))
    conn.commit()
    conn.close()


def update_journal_by_name(name, store):
    conn = connection()
    cursor = conn.cursor()
    sql = "update journals set store = %s where name=%s"
    cursor.execute(sql, (store, name,))
    conn.commit()
    conn.close()


def add_new_order_to_basket(user_id, order):
    conn = connection()
    cursor = conn.cursor()
    sql = 'insert into basket (user_id, `order`) values (%s,%s)'
    cursor.execute(sql, (user_id, order,))
    conn.commit()
    conn.close()


def add_order_to_basket(user_id, order):
    conn = connection()
    cursor = conn.cursor()
    sql = "update basket set `order` = %s where user_id = %s and achieve = %s "
    cursor.execute(sql, (order, user_id, False,))
    conn.commit()
    conn.close()


def add_price_to_basket(user_id, price):
    conn = connection()
    cursor = conn.cursor()
    sql = "update basket set price = %s where user_id = %s and achieve = %s "
    cursor.execute(sql, (price, user_id, False,))
    conn.commit()
    conn.close()


def add_paymenbt_type_to_basket(user_id, payment):
    conn = connection()
    cursor = conn.cursor()
    sql = "update basket set payment_type = %s where user_id = %s and achieve = %s "
    cursor.execute(sql, (payment, user_id, False,))
    conn.commit()
    conn.close()


def add_comment_to_basket(user_id, comment):
    conn = connection()
    cursor = conn.cursor()
    sql = "update basket set comment = %s where user_id = %s and achieve = %s"
    try:
        cursor.execute(sql, (comment, user_id, False,))
    except mysql.connector.errors.DatabaseError as e:
        print(e)
        comment2 = commands.clean_comment(comment)
        print(comment2)
        cursor.execute(sql, (comment2, user_id, False,))
    conn.commit()
    conn.close()


def add_delivery_date_to_basket(user_id, date):
    conn = connection()
    cursor = conn.cursor()
    sql = "update basket set `delivery_date` = %s where user_id = %s and achieve = %s "
    cursor.execute(sql, (date, user_id, False,))
    conn.commit()
    conn.close()


def get_basket_by_userid(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = 'select user_id, `order`, price, comment, `delivery_date`, payment_type, id from basket where user_id = %s and achieve = %s'
    cursor.execute(sql, (user_id, False,))
    basket = cursor.fetchone()
    conn.close()
    return basket


def set_basket_achieve_true(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = "update basket set achieve = %s where user_id = %s and achieve = %s"
    cursor.execute(sql, (True, user_id, False,))
    conn.commit()
    conn.close()


def get_user_data_by_userid(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = "select user_name, user_tel, user_email, user_adress from users where user_id = %s and accept = %s"
    cursor.execute(sql, (user_id, True,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


def unaccept_user_data(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set accept = %s where user_id = %s and accept = %s "
    cursor.execute(sql, (False, user_id, True))
    conn.commit()
    conn.close()


def accept_user_data(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set accept = %s where user_id = %s and accept = %s"
    cursor.execute(sql, (True, user_id, False,))
    conn.commit()
    conn.close()


def set_user_data_full_name(user_id, name):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set user_name = %s where user_id = %s and accept = %s"
    cursor.execute(sql, (name, user_id, False))
    conn.commit()
    conn.close()


def set_user_data_telephone(user_id, telephone):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set user_tel = %s where user_id = %s and accept = %s"
    cursor.execute(sql, (telephone, user_id, False,))
    conn.commit()
    conn.close()


def set_user_data_email(user_id, email):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set user_email = %s where user_id = %s and accept = %s"
    cursor.execute(sql, (email, user_id, False,))
    conn.commit()
    conn.close()


def set_user_data_adress(user_id, adress):
    conn = connection()
    cursor = conn.cursor()
    sql = "update users set user_adress = %s where user_id = %s and accept = %s"
    cursor.execute(sql, (adress, user_id, False,))
    conn.commit()
    conn.close()


def get_user_data_by_userid_unaccepted(user_id):
    conn = connection()
    cursor = conn.cursor()
    sql = "select user_name, user_tel, user_email, user_adress from users where user_id = %s and accept = %s "
    cursor.execute(sql, (user_id, False,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


def add_new_delivery_notification(order_number, user_id, delivery_number):
    conn = connection()
    cursor = conn.cursor()
    sql = "insert into notifications (order_number, user_id, delivery_number) VALUES (%s, %s, %s)"
    cursor.execute(sql, (order_number, user_id, delivery_number,))
    conn.commit()
    conn.close()


def get_notification_by_order_number(order_number):
    conn = connection()
    cursor = conn.cursor()
    sql = "select * from notifications where order_number = %s"
    cursor.execute(sql, (order_number,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data


def set_delivery_number_in_notification(order_number, delivery_number):
    conn = connection()
    cursor = conn.cursor()
    sql = "update notifications set delivery_number = %s where order_number = %s and notify =  %s"
    cursor.execute(sql, (delivery_number, order_number, False,))
    conn.commit()
    conn.close()


def get_not_send_notifications():
    conn = connection()
    cursor = conn.cursor()
    sql = "select * from notifications where notify = %s "
    cursor.execute(sql, (False,))
    user_data = cursor.fetchall()
    conn.close()
    return user_data


def set_notifications_sended(delivery_number):
    conn = connection()
    cursor = conn.cursor()
    sql = "update notifications set notify = %s where delivery_number = %s and notify = %s "
    cursor.execute(sql, (True, delivery_number, False,))
    conn.commit()
    conn.close()


def get_admins(rights):
    conn = connection()
    cursor = conn.cursor()
    sql = "select * from admins where rights = %s"
    cursor.execute(sql, (rights,))
    admins = cursor.fetchall()
    conn.close()
    return admins


def get_users_id():
    conn = connection()
    cursor = conn.cursor()
    sql = "select * from users"
    cursor.execute(sql)
    users_id = cursor.fetchall()
    conn.close()
    return users_id

def get_all_orders_from_basket():
    conn = connection()
    cursor = conn.cursor()
    sql = 'select * from basket'
    cursor.execute(sql)
    baskets = cursor.fetchall()
    conn.close()
    return baskets

def get_all_users():
    conn = connection()
    cursor = conn.cursor()
    sql = 'select * from users'
    cursor.execute(sql)
    users = cursor.fetchall()
    conn.close()
    return users
