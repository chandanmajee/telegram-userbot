from telethon import TelegramClient, events
import re
import os
import threading
import http.server
import socketserver
import requests
import time

# === Get from Environment Variables ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# === Channels ===
SOURCE_CHANNELS = os.getenv("SOURCE_CHANNELS").split(",")
SOURCE_CHANNELS = [int(x) if x.strip().isdigit() else x.strip() for x in SOURCE_CHANNELS]

DESTINATION_CHANNELS = os.getenv("DESTINATION_CHANNELS").split(",")
DESTINATION_CHANNELS = [x.strip() for x in DESTINATION_CHANNELS]

# === MQM Pattern ===
MQM_PATTERN = re.compile(r"\bMQM[A-Z0-9]{5,10}\b")

# === Telegram Client Session ===
client = TelegramClient("render_session_1_1", api_id, api_hash)

# === Web Server for Render Uptime ===
PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

class QuietHTTPRequestHandler(Handler):
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("0.0.0.0", PORT), QuietHTTPRequestHandler) as httpd:
        print(f"🌐 Web server running on port {PORT}")
        httpd.serve_forever()

# === Self-Ping to Keep Alive ===
def keep_alive():
    url = "https://your-bot-name.onrender.com"  # <<== Replace with your actual Render URL
    while True:
        try:
            res = requests.get(url)
            print("💓 Self-ping:", res.status_code)
        except Exception as e:
            print("❌ Self-ping error:", e)
        time.sleep(240)  # 4 minutes

# === Message Handler ===
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    message = event.message.message.strip()
    print(f"📩 New message: {message}")

    match = MQM_PATTERN.search(message)
    if match:
        code = match.group()
        print(f"✅ MQM code found: {code}")
        for dest in DESTINATION_CHANNELS:
            try:
                entity = await client.get_entity(dest)
                await client.send_message(entity, f"`{code}`", parse_mode="markdown")
                print(f"🚀 Sent `{code}` to {dest}")
            except Exception as e:
                print(f"❌ Error sending to {dest}: {e}")
    else:
        print("⛔ No MQM code found.")

# === /wake command ===
@client.on(events.NewMessage(pattern="/wake"))
async def wake(event):
    url = "https://your-bot-name.onrender.com"  # Replace this too
    try:
        r = requests.get(url)
        await event.reply(f"🚀 Bot pinged itself! Status: {r.status_code}")
    except Exception as e:
        await event.reply(f"❌ Wake error: {e}")

# === Start Everything ===
threading.Thread(target=start_server, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

async def main():
    print("🤖 Starting Telegram client...")
    await client.start(phone=phone_number)
    print("✅ Telegram client connected successfully!")
    print("👂 Listening for incoming messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
