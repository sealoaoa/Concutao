import telebot
import requests
import threading
import time
import os

BOT_TOKEN = "8351425430:AAGZQxBjK2L_D5y5-MdoTNdE1ZXrj5OmFg8"
ADMIN_IDS = [7138785294, 6915752059]

API_URL = "https://api-lc79-congthuc-vip-tuananh.onrender.com/api/taixiumd5"

bot = telebot.TeleBot(BOT_TOKEN)

tool_status = False
chat_id = None
last_session = None

history = []
win = 0
lose = 0

last_prediction = None

def is_admin(uid):
    return uid in ADMIN_IDS

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """🤖 TOOL TÀI XỈU LC79\n\n/battool → bật tool\n/tattool → tắt tool""")

@bot.message_handler(commands=['battool'])
def battool(message):
    global tool_status, chat_id
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Không có quyền")
        return
    tool_status = True
    chat_id = message.chat.id
    bot.send_message(chat_id, "✅ Tool đã bật")

@bot.message_handler(commands=['tattool'])
def tattool(message):
    global tool_status
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Không có quyền")
        return
    tool_status = False
    bot.send_message(message.chat.id, "⛔ Tool đã tắt")

def tool_loop():
    global last_session, win, lose, history, last_prediction
    while True:
        if tool_status and chat_id:
            try:
                r = requests.get(API_URL, timeout=10)
                js = r.json()
                data = js["data"]
                phien = data["Phiên"]
                ket = data["Kết"]
                x1 = data["Xúc xắc 1"]
                x2 = data["Xúc xắc 2"]
                x3 = data["Xúc xắc 3"]
                tong = data["Tổng"]
                du_doan = data["Dự đoán"]
                tin_cay = data["Độ tin cậy"]
                next_session = data["phien_hien_tai"]

                if phien != last_session:
                    if last_prediction:
                        if last_prediction == ket:
                            win += 1
                            history.append("✅")
                        else:
                            lose += 1
                            history.append("❌")
                        history = history[-15:]

                    last_prediction = du_doan
                    last_session = phien
                    total = win + lose
                    rate = round((win / total) * 100, 2) if total > 0 else 0
                    history_text = " ".join(history)

                    msg = (f"🎰 TOOL TÀI XỈU LC79\n\n"
                           f"📊 Phiên: {phien}\n"
                           f"🎲 Xúc xắc: {x1} • {x2} • {x3}\n"
                           f"🔢 Tổng: {tong}\n"
                           f"🎯 Kết quả: {ket}\n"
                           f"━━━━━━━━━━━━━━\n"
                           f"🔮 DỰ ĐOÁN PHIÊN {next_session}\n\n"
                           f"👉 {du_doan}\n\n"
                           f"📈 Độ tin cậy: {tin_cay}\n"
                           f"━━━━━━━━━━━━━━\n"
                           f"🏆 Thắng: {win}\n"
                           f"💀 Thua: {lose}\n"
                           f"📊 Winrate: {rate}%\n\n"
                           f"📜 Lịch sử:\n{history_text}")
                    bot.send_message(chat_id, msg)
            except Exception as e:
                print("API lỗi:", e)
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=tool_loop, daemon=True).start()
    print("Bot đang chạy...")
    bot.infinity_polling()
