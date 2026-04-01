
# ===== 実行確認（必ず最初にログに出る） =====
print("START SCRIPT", flush=True)

import requests
import pandas as pd
from datetime import datetime, date
import smtplib
from email.message import EmailMessage
import holidays
import os
import sys

# ==================================================
# 1. 祝日チェック（日本）
# ==================================================
jp_holidays = holidays.Japan()
today_date = date.today()

if today_date in jp_holidays:
    print(f"祝日({jp_holidays[today_date]})のため処理をスキップします", flush=True)
    sys.exit(0)

# ==================================================
# 2. 株価取得（TradingView）
# ==================================================
url = "https://scanner.tradingview.com/japan/scan"

payload = {
    "symbols": {
        "tickers": ["TSE:6779"],  # 日本電波工業
        "query": {"types": []}
    },
    "columns": ["open", "high", "low", "close", "volume"]
}

response = requests.post(url, json=payload)
response.raise_for_status()

data = response.json()["data"][0]["d"]
open_, high, low, close, volume = data

today_str = datetime.now().strftime("%Y-%m-%d")

# ==================================================
# 3. CSV作成（1日1行）
# ==================================================
df = pd.DataFrame([{
    "Date": today_str,
    "Open": open_,
    "High": high,
    "Low": low,
    "Close": close,
    "Volume": volume
}])

csv_filename = "ndk_stock_latest.csv"
df.to_csv(csv_filename, index=False)

print("CSV作成完了", flush=True)
print(df, flush=True)

# ==================================================
# 4. Gmail 送信設定（GitHub Secrets）
# ==================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

TO_EMAIL = "ito.mamoru@ndk.com"

# ==================================================
# 5. メール作成
# ==================================================
msg = EmailMessage()
msg["Subject"] = "NDK_STOCK_CSV_AUTO"
msg["From"] = GMAIL_USER
msg["To"] = TO_EMAIL

msg.set_content(
    f"""NDK 株価CSV 自動送信

日付: {today_str}

本メールには CSV ファイルを添付しています。
"""
)

with open(csv_filename, "rb") as f:
    msg.add_attachment(
        f.read(),
        maintype="text",
        subtype="csv",
        filename=csv_filename
    )

# ==================================================
# 6. メール送信
# ==================================================
with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    server.send_message(msg)

print("Gmail送信完了", flush=True)
