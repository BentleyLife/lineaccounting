import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import schedule
import threading
import time
import google_sheet

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
        TextSendMessage(text="📒 今天記帳了嗎？請輸入「項目 金額 付款方式」或「補 YYYY-MM-DD 項目 金額 付款方式" )
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

    # 判斷是否為補登格式：補 YYYY-MM-DD 項目 金額 付款方式
    if len(parts) == 5 and parts[0] == '補':
        date_str = parts[1]
        category = parts[2]
        amount = parts[3]
        payment = parts[4]
        if amount.isdigit():
            amount = int(amount)
            try:
                google_sheet.record_expense(category, amount, payment, date_str)
                reply = f"✅ 已補登：{date_str}｜{category}｜{amount}元｜{payment}"
            except Exception as e:
                reply = "❌ 補登失敗，請稍後再試。"
                print(f"Error writing to sheet: {e}")
        else:
            reply = "❗ 金額需為純數字，例如：補 2025-04-20 午餐 150 現金"

    # 標準記帳：項目 金額 付款方式
    elif len(parts) == 3 and parts[1].isdigit():
        category = parts[0]
        amount = int(parts[1])
        payment = parts[2]
        try:
            google_sheet.record_expense(category, amount, payment)
            reply = f"✅ 已記錄：{category}｜{amount}元｜{payment}"
        except Exception as e:
            reply = "❌ 記錄失敗，請稍後再試。"
            print(f"Error writing to sheet: {e}")
    else:
        reply = (
            "❗ 請輸入「項目 金額 付款方式」\n"
            "或「補 YYYY-MM-DD 項目 金額 付款方式」例如：補 2025-04-20 午餐 150 現金"
        )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == '__main__':
    app.run(port=5000)