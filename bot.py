# OGGY-VC-USERBOT - FINAL FIXED VERSION 😈🔥
# CHUMT KA PYASA - COMMANDS FIXED

import asyncio
import os
import json
import subprocess
import signal
import sys
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp
from youtubesearchpython import VideosSearch

# ==================== CONFIG ====================
API_ID = 38712417
API_HASH = "4b583e8882508b7db133f8502b7b105f"
SESSION = "ELUMTER_COPY_userbot"
PLAYLIST_FILE = "playlist.json"

# 🔥 APNI TELEGRAM USER ID DAAL
OWNER_ID = 123456789  # <-- YAHAN APNI ID DAAL!

# ==================== INIT ====================
app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)

queue = []
current_playing = None
saved_rc = {}
ffmpeg_process = None

if os.path.exists(PLAYLIST_FILE):
    with open(PLAYLIST_FILE, 'r') as f:
        saved_rc = json.load(f)

def save_rc():
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(saved_rc, f, indent=4)

# ==================== HELPERS ====================
async def get_audio_url(query):
    if query.startswith(('http://', 'https://')):
        return query
    try:
        search = VideosSearch(query, limit=1)
        result = await search.next()
        if result and result.get('result'):
            return f"https://youtube.com/watch?v={result['result'][0]['id']}"
    except Exception as e:
        print(f"Search error: {e}")
    return None

def get_stream_url(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                return info.get('url')
    except Exception as e:
        print(f"Stream error: {e}")
    return None

def stop_ffmpeg():
    global ffmpeg_process
    if ffmpeg_process:
        try:
            ffmpeg_process.terminate()
            ffmpeg_process.kill()
            ffmpeg_process = None
        except:
            pass

async def play_audio(chat_id, stream_url):
    global ffmpeg_process
    stop_ffmpeg()
    
    cmd = [
        'ffmpeg',
        '-i', stream_url,
        '-f', 's16le',
        '-ac', '2',
        '-ar', '48000',
        '-acodec', 'pcm_s16le',
        '-re',
        '-loglevel', 'quiet',
        'pipe:1'
    ]
    
    ffmpeg_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        await app.send_voice(chat_id, ffmpeg_process.stdout, duration=0)
    except Exception as e:
        print(f"Play error: {e}")

# ==================== OWNER CHECK ====================
async def is_owner(message):
    """Check if user is owner"""
    if message.from_user.id == OWNER_ID:
        return True
    await message.reply("❌ **You are not the owner!** 😡")
    return False

# ==================== COMMANDS (GROUP + PRIVATE) ====================

@app.on_message(filters.command(["start", "help"]))
async def start_cmd(client, message):
    if not await is_owner(message):
        return
    await message.reply(
        "🔥 **OGGY-VC-USERBOT ACTIVATED**\n\n"
        "**Commands:**\n"
        "`.joinvc chat_id` - VC join\n"
        "`.leavevc` - VC leave\n"
        "`.play query` - Play song\n"
        "`.skip` - Skip current\n"
        "`.stop` - Stop playing\n"
        "`.queue` - Show queue\n"
        "`.addrc name url` - Save RC\n"
        "`.show` - Show saved RC\n"
        "`.delrc name` - Delete RC\n"
        "`.ping` - Check status\n\n"
        "😈 CHUMT KA PYASA ACTIVE!"
    )

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    if not await is_owner(message):
        return
    start = datetime.now()
    await message.reply("🏓 Pinging...")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.reply(f"🏓 **Pong!** `{ms:.2f}ms`")

@app.on_message(filters.command("joinvc"))
async def join_vc(client, message):
    if not await is_owner(message):
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("🤡 Usage: `.joinvc group_id`")
            return
        
        chat_id = int(args[1])
        
        try:
            chat = await client.get_chat(chat_id)
            await message.reply(f"✅ **Joining VC...** `{chat.title if chat.title else chat_id}`")
        except:
            await message.reply(f"❌ **Chat not found!** Check ID 😡")
            return
        
        await client.join_chat(chat_id)
        await message.reply(f"✅ **VC Joined!** `{chat_id}` 😈")
        
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

@app.on_message(filters.command("leavevc"))
async def leave_vc(client, message):
    if not await is_owner(message):
        return
    try:
        args = message.text.split()
        chat_id = int(args[1]) if len(args) > 1 else message.chat.id
        
        stop_ffmpeg()
        global queue, current_playing
        queue.clear()
        current_playing = None
        
        await client.leave_chat(chat_id)
        await message.reply(f"✅ **Left VC!** `{chat_id}` 🚪")
        
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

@app.on_message(filters.command("play"))
async def play_music(client, message):
    if not await is_owner(message):
        return
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("🤡 Usage: `.play song_name`")
            return
        
        query = args[1]
        await message.reply("🔍 **Searching...** 🕵️")
        
        if query in saved_rc:
            url = saved_rc[query]
        else:
            url = await get_audio_url(query)
        
        if not url:
            await message.reply("❌ **No results!** 😡")
            return
        
        stream_url = get_stream_url(url)
        if not stream_url:
            await message.reply("❌ **Stream unavailable!** 😭")
            return
        
        global current_playing, queue
        
        if current_playing is None:
            await play_audio(message.chat.id, stream_url)
            current_playing = query
            await message.reply(f"▶️ **Now Playing:** `{query}` 😈🔥")
        else:
            queue.append({'query': query, 'stream_url': stream_url})
            await message.reply(f"⏳ **Added to Queue:** `{query}` (Position: {len(queue)}) 🎶")
            
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

@app.on_message(filters.command("skip"))
async def skip_song(client, message):
    if not await is_owner(message):
        return
    global queue, current_playing
    
    if not queue:
        await message.reply("📭 **Queue empty!**")
        return
    
    stop_ffmpeg()
    next_song = queue.pop(0)
    current_playing = next_song['query']
    
    try:
        await play_audio(message.chat.id, next_song['stream_url'])
        await message.reply(f"⏭️ **Now Playing:** `{next_song['query']}` (Queue: {len(queue)})")
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

@app.on_message(filters.command("stop"))
async def stop_music(client, message):
    if not await is_owner(message):
        return
    stop_ffmpeg()
    global current_playing, queue
    current_playing = None
    queue.clear()
    await message.reply("⏹️ **Stopped!** 🛑")

@app.on_message(filters.command("queue"))
async def show_queue(client, message):
    if not await is_owner(message):
        return
    if not queue:
        await message.reply("📭 **Queue is empty!**")
        return
    
    text = "📋 **QUEUE LIST**\n═══════\n"
    for i, song in enumerate(queue, 1):
        text += f"{i}. `{song['query']}`\n"
    await message.reply(text)

@app.on_message(filters.command("addrc"))
async def add_rc(client, message):
    if not await is_owner(message):
        return
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply("🤡 Usage: `.addrc name YouTube_URL`")
            return
        
        name, url = args[1], args[2]
        saved_rc[name] = url
        save_rc()
        await message.reply(f"✅ **RC Saved:** `{name}` 😈")
        
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

@app.on_message(filters.command("show"))
async def show_rc(client, message):
    if not await is_owner(message):
        return
    if not saved_rc:
        await message.reply("📭 **No saved RC!**")
        return
    
    text = "📋 **SAVED RC LIST**\n═══════\n"
    for i, (name, url) in enumerate(saved_rc.items(), 1):
        text += f"{i}. `{name}` → {url[:40]}...\n"
    await message.reply(text)

@app.on_message(filters.command("delrc"))
async def del_rc(client, message):
    if not await is_owner(message):
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("🤡 Usage: `.delrc name`")
            return
        
        name = args[1]
        if name in saved_rc:
            del saved_rc[name]
            save_rc()
            await message.reply(f"✅ **RC Deleted:** `{name}` 🗑️")
        else:
            await message.reply(f"❌ `{name}` not found!")
            
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

# ==================== UNKNOWN COMMAND HANDLER ====================
@app.on_message(filters.command([]))
async def unknown_cmd(client, message):
    if message.text and message.text.startswith('.'):
        if message.from_user.id == OWNER_ID:
            await message.reply("❌ **Unknown command!** Use `.start` to see all commands 😡")

# ==================== DEBUG LOG ====================
@app.on_message(filters.text & filters.private)
async def debug_log(client, message):
    if message.text and message.text.startswith('.'):
        print(f"📩 Command received: {message.text} from {message.from_user.id}")
        if message.from_user.id != OWNER_ID:
            await message.reply(f"❌ Owner ID mismatch!\nYour ID: `{message.from_user.id}`\nOwner ID: `{OWNER_ID}`")

# ==================== RUN ====================
async def main():
    print("🔥 OGGY-VC-USERBOT STARTING...")
    print("😈 CHUMT KA PYASA ACTIVATED!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("📱 Commands work in BOTH Group and Private!")
    
    await app.start()
    me = await app.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username})")
    print(f"📱 Bot User ID: {me.id}")
    print("\n🎵 Bot is running! Send commands in Telegram.")
    print("Commands: .start, .joinvc, .play, .skip, .stop, .queue, .addrc, .show, .delrc")
    print("\n⚠️ If command doesn't work, check terminal for errors!")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n❌ Bot stopped!")
        stop_ffmpeg()
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        stop_ffmpeg()
