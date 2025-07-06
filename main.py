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
SOURCE_CHANNELS = [x.strip() for x in SOURCE_CHANNELS]
DESTINATION_CHANNELS = os.getenv("DESTINATION_CHANNELS").split(",")
DESTINATION_CHANNELS = [x.strip() for x in DESTINATION_CHANNELS]

# === Pattern to Detect MQM Code ===
MQM_PATTERN = re.compile(r"\bMQM[A-Z0-9]{5,10}\b")

# === Telegram Client with Session ===
client = TelegramClient("render_session_1_1", api_id, api_hash)

# === Resolve valid source channels dynamically ===
async def resolve_valid_channels():
    valid_sources = []
    for source in SOURCE_CHANNELS:
        try:
            entity = await client.get_entity(source)
            valid_sources.append(entity)
            print(f"✅ Valid source: {source}")
        except Exception as e:
            print(f"❌ Invalid source channel: {source} — {e}")
    return valid_sources

# === Web Server for Uptime (Render/Replit) ===
PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

class QuietHTTPRequestHandler(Handler):
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("0.0.0.0", PORT), QuietHTTPRequestHandler) as httpd:
        print(f"🌐 Web server running on port {PORT}")
        httpd.serve_forever()

# Start Web Server
thread = threading.Thread(target=start_server)
thread.daemon = True
thread.start()

# === Main Bot Logic ===
async def main():
    print("🤖 Starting Telegram client...")
    await client.start(phone=phone_number)
    print("✅ Telegram client connected successfully!")

    valid_sources = await resolve_valid_channels()

    @client.on(events.NewMessage(chats=valid_sources))
    async def handler(event):
        if not event.message or not event.message.message:
            return
        message = event.message.message.strip()
        print(f"📥 New Message: {message}")

        match = MQM_PATTERN.search(message)
        if match:
            code = match.group()
            print(f"✅ Found MQM Code: {code}")
            for dest in DESTINATION_CHANNELS:
                try:
                    entity = await client.get_entity(dest)
                    await client.send_message(entity, f"`{code}`", parse_mode="markdown")
                    print(f"🚀 Sent to {dest}")
                except Exception as e:
                    print(f"❌ Failed to send to {dest}: {e}")
        else:
            print("⛔ No MQM code found.")

    print("👂 Listening for messages...")
    await client.run_until_disconnected()

# === Run Bot ===
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
