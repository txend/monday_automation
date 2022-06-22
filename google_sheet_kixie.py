# [START sheets_quickstart]
from __future__ import print_function

from google.oauth2 import service_account
import gspread
import re

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'key.json'


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1js9D6WJSm5cY_Od6Bb63HZzPr-H3tuWXDFOBwI01iO4'

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# If modifying these scopes, delete the file token.json.

def clean_phone(phone_number):
    string1 = phone_number
    clean_phone = str(re.search(r'\d+', string1).group())
    return clean_phone


def find_client(phone_number):

    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(SAMPLE_SPREADSHEET_ID) # or by sheet name: gc.open("TestList")
    worksheet = sh.sheet1

    phone_number = clean_phone(phone_number)

    columns_name = worksheet.row_values(1)

    location  = worksheet.find(phone_number)
    if location is None:
        return
    row_data = worksheet.row_values(location.row)
    temp_dict = {}
    for c,d in zip(columns_name, row_data):
        temp_dict[c] = d
    return temp_dict



# print(find_client('15026901111', worksheet, columns_name))



