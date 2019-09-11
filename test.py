from oauth2client.service_account import ServiceAccountCredentials
import gspread
from config import config

ORDER_KEY = config.order_key
def get_journals_from_docks():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('config/client_secret.json', scope)
    client = gspread.authorize(creds)
    # Find a workbook by key and open the first sheet
    sheet = client.open_by_key(ORDER_KEY).get_worksheet(1)
    result = sheet.get_all_values()
    result = result[1:]
    result = result[0][0].encode('ascii', 'ignore').decode('ascii')
    return result

a = get_journals_from_docks()
print(a)