#!/usr/bin/env python3
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
import os

# ─── CONFIG ────────────────────────────────────────────────────────────────────
API_ID    = 29987885
API_HASH  = "38e7dccee55f49d40a5a5a7e08549442"
BOT_TOKEN = "7948982537:AAEhv6pZ2zZdhXu1AdruYWwXX0LDBfPIpKo"
DOWNLOADS = "downloads"   # folder for temp files
# ────────────────────────────────────────────────────────────────────────────────

# Ensure download directory exists
os.makedirs(DOWNLOADS, exist_ok=True)

app = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
def start_cmd(client, message):
    message.reply_text(
        "👋 Send me a TikTok or Facebook video URL and I'll download it for you!"
    )

@app.on_message(filters.text & ~filters.command("start"))
def download_handler(client, message):
    url = message.text.strip()
    if "tiktok.com" in url or "vt.tiktok.com" in url:
        platform = "TikTok"
    elif "facebook.com" in url or "fb.watch" in url:
        platform = "Facebook"
    else:
        return message.reply_text("❌ Please send a valid TikTok or Facebook video URL.")

    status = message.reply_text(f"⬇️ Downloading your {platform} video… please wait.")
    print(f"[INFO] Download requested for {platform}: {url}")

    try:
        ydl_opts = {
            "format": "mp4",
            "outtmpl": os.path.join(DOWNLOADS, "%(id)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        print(f"[INFO] Download complete: {filename}")

        if not os.path.exists(filename):
            raise FileNotFoundError(f"Downloaded file not found: {filename}")

        filesize = os.path.getsize(filename)
        print(f"[INFO] File size: {filesize} bytes")

        # Telegram max video size is ~50MB for send_video
        if filesize < 50 * 1024 * 1024:
            client.send_video(
                chat_id=message.chat.id,
                video=filename,
                caption=f"✅ Here’s your {platform} video!"
            )
            print(f"[INFO] Sent as video.")
        else:
            client.send_document(
                chat_id=message.chat.id,
                document=filename,
                caption=f"✅ Here’s your {platform} video (file)!"
            )
            print(f"[INFO] Sent as document due to size.")

        status.delete()
        os.remove(filename)
        print(f"[INFO] Cleaned up: {filename}")

    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        try:
            status.edit(f"🚫 Download failed:\n{e}")
        except:
            message.reply_text(f"🚫 Download failed:\n{e}")

if __name__ == "__main__":
    print("[INFO] Starting bot…")
    app.run()
    print("[INFO] Bot stopped.")
