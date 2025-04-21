import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import schedule
import threading
import time
import google_sheet  # 自己的模組

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
USER_ID = os.getenv('USER_ID')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 每天晚上 22:00 自動提醒
schedule.every().day.at("22:00").do(
    lambda: line_bot_api.push_message(
        USER_ID,
        TextSendMessage(text="今天記帳了嗎？請輸入「名稱 金額」來記帳！💰")
    )
)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    parts = text.split()
    # 支援「名稱 金額」格式
    if len(parts) == 2 and parts[1].isdigit():
        name = parts[0]
        amount = int(parts[1])
        try:
            google_sheet.record_expense(name, amount)
            reply = f"已記錄：{name} {amount} 元到 Google Sheet ✅"
        except Exception as e:
            reply = "記錄失敗，請稍後再試。"
            print(f"Error writing to sheet: {e}")
    else:
        reply = "請輸入「名稱 金額」的格式，例如：午餐 150"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == '__main__':
    app.run(port=5000)