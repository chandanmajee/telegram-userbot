from telethon import TelegramClient, events
import re
import threading
import http.server
import socketserver
import os

# === Get from Environment Variables ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# Source and Destination Channels
SOURCE_CHANNELS = os.getenv("SOURCE_CHANNELS").split(",")
SOURCE_CHANNELS = [int(x) if x.isdigit() else x.strip() for x in SOURCE_CHANNELS]

DESTINATION_CHANNELS = os.getenv("DESTINATION_CHANNELS").split(",")
DESTINATION_CHANNELS = [x.strip() for x in DESTINATION_CHANNELS]

# === Pattern to Detect MQM Code ===
MQM_PATTERN = re.compile(r"\bMQM[A-Z0-9]{5,10}\b")

# === Telegram Client with Session ===
client = TelegramClient("render_session_1", api_id, api_hash)

# === Message Handler ===
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    try:
        message = event.message.message.strip()
        print(f"📥 New Message Received: {message}")

        match = MQM_PATTERN.search(message)
        if match:
            code = match.group()
            print(f"✅ MQM Code Detected: {code}")

            for dest in DESTINATION_CHANNELS:
                try:
                    entity = await client.get_entity(dest)
                    await client.send_message(entity, f"`{code}`", parse_mode="markdown")
                    print(f"🚀 Sent code `{code}` to {dest}")
                except Exception as e:
                    print(f"❌ Error sending to {dest}: {e}")
        else:
            print("⛔ No MQM code found in message.")
    except Exception as e:
        print(f"❗ Handler Error: {e}")

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

# === Start Web Server Thread ===
thread = threading.Thread(target=start_server)
thread.daemon = True
thread.start()

# === Start Telegram Bot ===
async def main():
    print("🤖 Starting Telegram client...")
    await client.start(phone=phone_number)
    print("✅ Telegram client connected successfully!")
    print("👂 Listening for incoming messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
