# OGGY-VC-USERBOT - PYTHON 3.9 COMPATIBLE 😈🔥
# CHUMT KA PYASA - WORKING VERSION

import asyncio
import sys
import os
import json
from datetime import datetime

# ============ EVENT LOOP FIX ============
if sys.version_info >= (3, 10):
    try:
        import uvloop
        uvloop.install()
    except:
        pass

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp
from youtubesearchpython import VideosSearch

# ==================== CONFIG ====================
API_ID = int(os.environ.get("API_ID", 38712417))
API_HASH = os.environ.get("API_HASH", "4b583e8882508b7db133f8502b7b105f")
SESSION = os.environ.get("SESSION", "ELUMTER_COPY_userbot")
PLAYLIST_FILE = "playlist.json"

# ==================== INIT ====================
app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)
call = PyTgCalls(app)

queue = []
current_playing = None
saved_rc = {}

# Load saved RC
if os.path.exists(PLAYLIST_FILE):
    with open(PLAYLIST_FILE, 'r') as f:
        saved_rc = json.load(f)

# ==================== HELPERS ====================
def save_rc():
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(saved_rc, f, indent=4)

async def get_audio_url(query):
    """YouTube search ya direct URL"""
    if query.startswith(('http://', 'https://')):
        return query
    
    search = VideosSearch(query, limit=1)
    result = await search.next()
    if result and result['result']:
        return f"https://youtube.com/watch?v={result['result'][0]['id']}"
    return None

async def get_stream_url(url):
    """Direct audio stream URL"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for f in info['formats']:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    return f['url']
        return None
    except Exception as e:
        print(f"Stream error: {e}")
        return None

async def play_next(chat_id):
    global queue, current_playing
    
    if not queue:
        current_playing = None
        return False
    
    next_song = queue.pop(0)
    current_playing = next_song['query']
    
    try:
        await call.change_stream(
            chat_id,
            AudioPiped(next_song['stream_url'])
        )
        return True
    except:
        return False

# ==================== COMMANDS ====================

@app.on_message(filters.command("start") & filters.me)
async def start_cmd(client, message):
    await message.edit(
        "🔥 **OGGY-VC-USERBOT ACTIVATED**\n\n"
        "**Commands:**\n"
        "`.joinvc chat_id` - VC join\n"
        "`.leavevc` - VC leave\n"
        "`.play query` - Play song\n"
        "`.skip` - Skip current\n"
        "`.pause` - Pause\n"
        "`.resume` - Resume\n"
        "`.queue` - Show queue\n"
        "`.addrc name url` - Save RC\n"
        "`.show` - Show saved RC\n"
        "`.delrc name` - Delete RC\n"
        "`.ping` - Check status\n\n"
        "😈 CHUMT KA PYASA ACTIVE!"
    )

@app.on_message(filters.command("ping") & filters.me)
async def ping_cmd(client, message):
    start = datetime.now()
    await message.edit("🏓 Pinging...")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f"🏓 **Pong!** `{ms:.2f}ms`\n😈 OGGY AI is alive!")

@app.on_message(filters.command("joinvc") & filters.me)
async def join_vc(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.edit("🤡 Usage: `.joinvc group_id`")
            return
        
        chat_id = int(args[1]) if args[1].isdigit() else args[1]
        
        await call.join_group_call(
            chat_id,
            AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"),
            AudioQuality.MEDIUM
        )
        
        await message.edit(f"✅ **VC Joined!** 🎧\nChat: `{chat_id}`\n😈 CHUMT KA GANA AA RAHA!")
        
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("leavevc") & filters.me)
async def leave_vc(client, message):
    try:
        args = message.text.split()
        chat_id = int(args[1]) if len(args) > 1 else message.chat.id
        
        await call.leave_group_call(chat_id)
        global queue, current_playing
        queue.clear()
        current_playing = None
        
        await message.edit(f"✅ **Left VC!** 🚪\nChat: `{chat_id}`\n😈 TATA BYE BYE!")
        
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("play") & filters.me)
async def play_music(client, message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("🤡 Usage: `.play song_name ya URL`")
            return
        
        query = args[1]
        await message.edit("🔍 **Searching...** 🕵️")
        
        # Check if query is saved RC
        if query in saved_rc:
            url = saved_rc[query]
        else:
            url = await get_audio_url(query)
        
        if not url:
            await message.edit("❌ **No results!** 😡")
            return
        
        stream_url = await get_stream_url(url)
        if not stream_url:
            await message.edit("❌ **Stream unavailable!** 😭")
            return
        
        global current_playing, queue
        
        if current_playing is None:
            await call.change_stream(
                message.chat.id,
                AudioPiped(stream_url)
            )
            current_playing = query
            await message.edit(f"▶️ **Now Playing:** `{query}`\n🎵 CHUMT KA GANA 😈🔥")
        else:
            queue.append({
                'query': query,
                'url': url,
                'stream_url': stream_url
            })
            await message.edit(f"⏳ **Added to Queue:** `{query}`\nPosition: `{len(queue)}` 🎶")
            
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("skip") & filters.me)
async def skip_song(client, message):
    global current_playing, queue
    
    if not queue:
        await message.edit("📭 **Queue empty!** Kuch daal pehle 😭")
        return
    
    next_song = queue.pop(0)
    current_playing = next_song['query']
    
    try:
        await call.change_stream(
            message.chat.id,
            AudioPiped(next_song['stream_url'])
        )
        await message.edit(f"⏭️ **Skipped!** Now playing: `{next_song['query']}`\nQueue: `{len(queue)}` songs 😈")
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("pause") & filters.me)
async def pause_vc(client, message):
    try:
        await call.pause_stream(message.chat.id)
        await message.edit("⏸️ **Paused!** `.resume` se chalao 🥀")
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("resume") & filters.me)
async def resume_vc(client, message):
    try:
        await call.resume_stream(message.chat.id)
        await message.edit("▶️ **Resumed!** CHUMT KA GANA 😈🔥")
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("queue") & filters.me)
async def show_queue(client, message):
    if not queue:
        await message.edit("📭 **Queue is empty!**")
        return
    
    text = "📋 **QUEUE LIST**\n═══*\n"
    for i, song in enumerate(queue, 1):
        text += f"{i}. `{song['query']}`\n"
    
    await message.edit(text)

@app.on_message(filters.command("addrc") & filters.me)
async def add_rc(client, message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.edit("🤡 Usage: `.addrc name YouTube_URL`")
            return
        
        name, url = args[1], args[2]
        saved_rc[name] = url
        save_rc()
        
        await message.edit(f"✅ **RC Saved!** `{name}` → {url[:40]}...\nPlay: `.play {name}` 😈")
        
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("show") & filters.me)
async def show_rc(client, message):
    if not saved_rc:
        await message.edit("📭 **No saved RC!** `.addrc` use karo 😭")
        return
    
    text = "📋 **SAVED RC LIST**\n═══*\n"
    for i, (name, url) in enumerate(saved_rc.items(), 1):
        text += f"{i}. `{name}` → {url[:40]}...\n"
    
    await message.edit(text)

@app.on_message(filters.command("delrc") & filters.me)
async def del_rc(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.edit("🤡 Usage: `.delrc name`")
            return
        
        name = args[1]
        if name in saved_rc:
            del saved_rc[name]
            save_rc()
            await message.edit(f"✅ **RC Deleted:** `{name}` 🗑️")
        else:
            await message.edit(f"❌ `{name}` not found! `.show` dekh 😡")
            
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

# ==================== RUN ====================
async def main():
    print("🔥 OGGY-VC-USERBOT STARTING...")
    print("😈 CHUMT KA PYASA ACTIVATED!")
    
    await call.start()
    await app.start()
    
    print("✅ Bot is running! Use commands in Telegram.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n❌ Bot stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")
