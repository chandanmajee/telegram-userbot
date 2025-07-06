from telethon import TelegramClient, events
import re, os, threading, http.server, socketserver

# === Environment Variables ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# === Channels ===
SOURCE_CHANNELS = os.getenv("SOURCE_CHANNELS").split(",")
SOURCE_CHANNELS = [int(x) if x.isdigit() else x.strip() for x in SOURCE_CHANNELS]
DESTINATION_CHANNELS = os.getenv("DESTINATION_CHANNELS").split(",")
DESTINATION_CHANNELS = [int(x) if x.isdigit() else x.strip() for x in DESTINATION_CHANNELS]

# === MQM Code Pattern ===
MQM_PATTERN = re.compile(r"\bMQM[A-Z0-9]{5,10}\b")

# === Telegram Client ===
client = TelegramClient("render_session_1", api_id, api_hash)

# === Message Handler ===
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def fast_forward(event):
    msg = event.message.message or ""
    match = MQM_PATTERN.search(msg.strip())

    if match:
        code = match.group()
        for dest in DESTINATION_CHANNELS:
            try:
                await client.send_message(dest, f"`{code}`", parse_mode="markdown")
                print(f"🚀 Sent to {dest}: `{code}`")
            except Exception as e:
                print(f"❌ Error to {dest}: {e}")
    else:
        print("⏩ Skipped (no MQM code)")

# === Tiny Web Server for Render Uptime ===
class NoLogHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

def start_web():
    with socketserver.TCPServer(("0.0.0.0", 8080), NoLogHandler) as httpd:
        print("🌐 Web server running on 8080")
        httpd.serve_forever()

threading.Thread(target=start_web, daemon=True).start()

# === Start Client ===
async def main():
    print("🤖 Connecting...")
    await client.start(phone=phone_number)
    print("✅ Bot is ready!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
