from oauth2client.service_account import ServiceAccountCredentials
import gspread
from config import config
import db

ORDER_KEY = config.order_key
def get_journals_from_docks():
    journal_in_db = db.get_journal_by_name('Херсон')
    return journal_in_db
a = get_journals_from_docks()
print(a[0])