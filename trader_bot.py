import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

# Your exact Telegram credentials
BOT_TOKEN = "8989772990:AAGk_LwE2Q-ddvivtMhfuNVuF793aEgERbM"
CHAT_ID = "6960001622"

# ---------- 1. Render Keep-Alive Server ----------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"XAUUSD 5-TP Cloud Bot is live and running!")

    def log_message(self, format, *args):
        return

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# ---------- 2. Telegram Alert Function ----------
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram error: {e}")

# ---------- 3. Live Price Fetcher ----------
def get_live_gold_price():
    try:
        url = "https://api.goldprice.dev/v1/prices?symbol=XAU-USD-SPOT"
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            return float(data["symbols"][0]["price"])
    except Exception as e:
        print(f"Error fetching price: {e}")
    return None

# ---------- 4. Automated Signal & 5-TP Calculator ----------
def market_monitor_loop():
    print("📈 Cloud XAUUSD 5-TP Monitor started...")
    last_price = get_live_gold_price()
    
    if last_price:
        send_telegram_alert(f"🟢 *XAUUSD Bot Online with 5-TP System!*\nBaseline Price: `${last_price:.2f}`")

    while True:
        current_price = get_live_gold_price()
        if current_price and last_price:
            price_change = current_price - last_price
            
            # Trigger threshold ($3+ shift)
            if abs(price_change) >= 3.0:
                is_buy = price_change > 0
                direction = "🟢 **BUY (LONG)**" if is_buy else "🔴 **SELL (SHORT)**"
                
                # Calculate Stop Loss and 5 Safe Take Profits
                if is_buy:
                    sl = current_price - 8.0
                    tp1 = current_price + 3.0
                    tp2 = current_price + 6.0
                    tp3 = current_price + 9.0
                    tp4 = current_price + 12.0
                    tp5 = current_price + 15.0
                else:
                    sl = current_price + 8.0
                    tp1 = current_price - 3.0
                    tp2 = current_price - 6.0
                    tp3 = current_price - 9.0
                    tp4 = current_price - 12.0
                    tp5 = current_price - 15.0

                # Formulate Professional Signal Message
                alert_msg = (
                    f"🚨 *XAUUSD MARKET SIGNAL DETECTED* 🚨\n\n"
                    f"• **Direction:** {direction}\n"
                    f"• **Entry Price:** `${current_price:.2f}`\n"
                    f"• **Stop Loss (SL):** `${sl:.2f}`\n\n"
                    f"🎯 **Safe Take Profit Levels:**\n"
                    f"  1️⃣ **TP 1:** `${tp1:.2f}`\n"
                    f"  2️⃣ **TP 2:** `${tp2:.2f}`\n"
                    f"  3️⃣ **TP 3:** `${tp3:.2f}`\n"
                    f"  4️⃣ **TP 4:** `${tp4:.2f}`\n"
                    f"  5️⃣ **TP 5:** `${tp5:.2f}`\n\n"
                    f"⚡ *Manage risk properly and scale out lots at each TP!*"
                )
                
                send_telegram_alert(alert_msg)
                last_price = current_price  # Reset baseline after firing alert
                
        # Check every 60 seconds
        time.sleep(60)

if __name__ == "__main__":
    market_monitor_loop()
