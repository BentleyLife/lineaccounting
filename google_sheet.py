import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Google API 權限範圍
def get_scope():
    return [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

# 服務金鑰檔名
CREDS_FILE = 'credentials.json'
# 你的 Google Sheet ID
SPREADSHEET_ID = '1x4341FSJsWA_-t5wIfAkjVVngnGiX6TeXUvjcdVpZBQ'

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, get_scope())
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.sheet1  # 第一個工作表

def record_expense(name: str, amount: int):
    ws = connect_sheet()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # 依序寫入：日期、名稱、金額
    ws.append_row([today, name, amount])
