from telethon import TelegramClient, events
import re
import threading
import http.server
import socketserver
import os

=== Get from Environment Variables ===

api_id = int(os.getenv("API_ID")) api_hash = os.getenv("API_HASH") phone_number = os.getenv("PHONE_NUMBER")

SOURCE_CHANNELS = os.getenv("SOURCE_CHANNELS").split(",") SOURCE_CHANNELS = [int(x) if x.isdigit() else x for x in SOURCE_CHANNELS]

DESTINATION_CHANNELS = os.getenv("DESTINATION_CHANNELS").split(",") DESTINATION_CHANNELS = [int(x) if x.isdigit() else x for x in DESTINATION_CHANNELS]

=== Pattern to Detect MQM Code ===

MQM_PATTERN = re.compile(r"\bMQM[A-Z0-9]{5,10}\b")

=== Telegram Client ===

client = TelegramClient("render_session_1", api_id, api_hash)

=== Message Handler ===

@client.on(events.NewMessage(chats=SOURCE_CHANNELS)) async def handler(event): message = event.message.message.strip()

match = MQM_PATTERN.search(message)
if match:
    code = match.group()
    for dest in DESTINATION_CHANNELS:
        try:
            entity = await client.get_entity(dest)
            await client.send_message(entity, f"`{code}`", parse_mode="markdown")  # Mono-style
            print(f"✅ Sent clean code: {code} to {dest}")
        except Exception as e:
            print(f"❌ Error sending to {dest}: {e}")
else:
    print("⛔ No real code found, skipped message.")

=== Web Server for Uptime (Render) ===

PORT = 8080 Handler = http.server.SimpleHTTPRequestHandler

class QuietHTTPRequestHandler(Handler): def log_message(self, format, *args): pass

def start_server(): with socketserver.TCPServer(("0.0.0.0", PORT), QuietHTTPRequestHandler) as httpd: print(f"🌐 Web server running on port {PORT}") httpd.serve_forever()

Start Web Server

thread = threading.Thread(target=start_server) thread.daemon = True thread.start()

=== Start Telegram Bot ===

async def main(): print("🤖 Starting Telegram bot...") await client.start(phone=phone_number) print("✅ Bot connected successfully!") print("🗣️ Listening for messages...") await client.run_until_disconnected()

if name == "main": with client: client.loop.run_until_complete(main())

