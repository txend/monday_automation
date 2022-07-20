# [START sheets_quickstart]
from __future__ import print_function

from google.oauth2 import service_account
import gspread
import re
from config import get_env

app_config = get_env()

#google sheet scope
SCOPES = app_config.SCOPES

# google service_account file keys path
SERVICE_ACCOUNT_FILE = app_config.GOOGLE_SHEET_KEYS_PATH


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = app_config.SAMPLE_SPREADSHEET_ID

credentials = None
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# If modifying these scopes, delete the file token.json.


def clean_phone(phone_number):
    string1 = phone_number
    clean_phone = str(re.search(r"\d+", string1).group())
    return clean_phone


def find_client(phone_number):

    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    print('filename------->', SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(SAMPLE_SPREADSHEET_ID)  # or by sheet name: gc.open("TestList")
    worksheet = sh.sheet1

    phone_number = clean_phone(phone_number)

    columns_name = worksheet.row_values(1)

    location = worksheet.find(phone_number)
    if location is None:
        return
    row_data = worksheet.row_values(location.row)
    contact = {}
    deal={}
    org={}
    for c, d in zip(columns_name, row_data):
        if "contact" in c.split('_'):
            key = '_'.join(c.split('_')[1:])
            contact[key] = d
            # temprory logic to show contact id on first name
            if key == 'contact_id':
                contact['last_name'] = d

        if "deal" in c.split('_'):
            key = '_'.join(c.split('_')[1:])
            deal[key] = d

        if "org" in c.split('_'):
            key = '_'.join(c.split('_')[1:])
            org[key] = d

    result_dict = {
        "contact": contact,
        "deal": deal,
        "org": org
    }
    return result_dict


# find_client("+15598887642")