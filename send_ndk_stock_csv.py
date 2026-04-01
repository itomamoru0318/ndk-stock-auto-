
print("START SCRIPT", flush=True)

import requests
import pandas as pd
from datetime import datetime, date
import smtplib
from email.message import EmailMessage
import holidays
import os
import sys

# ===== 祝日チェック =====
jp_holidays = holidays.Japan()
today_date = date.today()

if today_date in jp_holidays:
    print(f"祝日({jp_holidays[today_date]})のため処理をスキップします", flush=True)
    sys.exit(0)

# ===== 株価取得（TradingView）=====
url = "https://scanner.tradingview.com/japan/scan"

payload = {
    "symbols": {
        "tickers": ["TSE:6779"],
        "query": {"types": []}
    },
    "columns": ["open", "high", "low", "close", "volume"]
}

res = requests.post(url, json=payload)
res.raise_for_status()

open_, high, low, close, volume = res.json()["data"][0]["d"]
today_str = datetime.now().strftime("%Y-%m-%d")

# ===== CSV作成 =====
df = pd.DataFrame([{
    "Date": today_str,
    "Open": open_,
    "High": high,
    "Low": low,
    "Close": close,
    "Volume": volume
}])

csv_path = "ndk_stock_latest.csv"
df.to_csv(csv_path, index=False)

print("CSV作成完了", flush=True)

# ===== Gmail送信 =====
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_APP_PASSWORD"]

TO_EMAIL = "ito.mamoru@ndk.com"

msg = EmailMessage()
msg["Subject"] = "NDK_STOCK_CSV_AUTO"
msg["From"] = GMAIL_USER
msg["To"] = TO_EMAIL

msg.set_content(f"NDK 株価CSV自動送信\n日付: {today_str}")

with open(csv_path, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="text",
        subtype="csv",
        filename="ndk_stock_latest.csv"
    )

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASS)
    server.send_message(msg)

print("Gmail送信完了", flush=True)

