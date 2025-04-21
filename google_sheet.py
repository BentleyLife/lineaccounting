import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# 權限範圍
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
# 金鑰檔名
CREDS_FILE = 'credentials.json'
# 試算表 ID
SPREADSHEET_ID = '你的-Sheet-ID'

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
    return sheet.sheet1

# record_expense 支援可傳入自訂日期 (date_str) 或使用今日
# signature: category, amount, payment, date_str=None

def record_expense(category: str, amount: int, payment: str, date_str: str=None):
    ws = connect_sheet()
    if date_str:
        date = date_str
    else:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    month = date[:7]  # YYYY-MM
    # 日期、月份、分類、金額、付款方式
    ws.append_row([date, month, category, amount, payment])