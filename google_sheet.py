import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Google API 權限範圍
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
# 服務金鑰檔名
CREDS_FILE = 'credentials.json'
# 你的 Google Sheet ID
SPREADSHEET_ID = '1x4341FSJsWA_-t5wIfAkjVVngnGiX6TeXUvjcdVpZBQ'

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.sheet1  # 第一個工作表

def record_expense(amount: int):
    ws = connect_sheet()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    ws.append_row([today, amount])