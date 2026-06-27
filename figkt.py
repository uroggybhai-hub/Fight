# OGGY-VC-USERBOT - RENDER FIXED VERSION 😈🔥
# CHUMT KA PYASA - EVENT LOOP FIX + TGCrypto SUPPORT

# ============= EVENT LOOP FIX (PEHLE IMPORT) =============
import asyncio
import uvloop
uvloop.install()  # CRITICAL: Yeh pehle run hona chahiye

import os
import re
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality, Stream
from pytgcalls.types.input_stream import AudioPiped, AudioRaw
import yt_dlp
from youtubesearchpython import VideosSearch

# ============= CONFIG =============
SESSION_FILE = "ELUMTER_COPY_userbot"  # Session file name
API_ID = 38712417  # Apna API ID
API_HASH = "4b583e8882508b7db133f8502b7b105f"  # Apna API Hash
PLAYLIST_FILE = "playlist.json"  # RC saved playlist

# ============= INIT =============
app = Client(
    SESSION_FILE,
    api_id=API_ID,
    api_hash=API_HASH
)

call = PyTgCalls(app)
queue = []
current_playing = None
saved_rc = {}  # {rc_name: url}

# Load saved RC
if os.path.exists(PLAYLIST_FILE):
    with open(PLAYLIST_FILE, 'r') as f:
        saved_rc = json.load(f)

# ============= HELPERS =============
def save_rc():
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(saved_rc, f, indent=4)

async def get_audio_url(query):
    """YouTube search aur direct URL get karo"""
    try:
        # Agar direct URL hai toh
        if query.startswith(('http://', 'https://')):
            return query
            
        # Search karo
        search = VideosSearch(query, limit=1)
        result = await search.next()
        if result and result['result']:
            url = f"https://youtube.com/watch?v={result['result'][0]['id']}"
            return url
        return None
    except Exception as e:
        print(f"Search error: {e}")
        return None

async def get_stream_url(url):
    """YouTube se direct audio stream URL nikaalo"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
        'audioformat': 'mp3',
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

# ============= COMMANDS =============

@app.on_message(filters.command("joinvc") & filters.me)
async def join_vc(client: Client, message: Message):
    """.joinvc group_id - Voice chat mein join karo"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.edit("🤡 Usage: `.joinvc group_id` ya channel_id")
            return
            
        chat_id = int(args[1]) if args[1].isdigit() else args[1]
        
        # Check karo chat exists
        try:
            chat = await client.get_chat(chat_id)
        except:
            await message.edit("❌ Chat nahi mila! ID sahi daal be.")
            return
            
        # Join VC
        await call.join_group_call(
            chat_id,
            AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"),  # Temp stream
            AudioQuality.MEDIUM
        )
        
        await message.edit(f"✅ VC join kar liya `{chat.title if hasattr(chat, 'title') else chat_id}` 😈")
        
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}` 😭")

@app.on_message(filters.command("levevc") & filters.me)
async def leave_vc(client: Client, message: Message):
    """.levevc - VC chhod do"""
    try:
        args = message.text.split()
        chat_id = message.chat.id
        
        if len(args) > 1:
            chat_id = int(args[1]) if args[1].isdigit() else args[1]
        
        await call.leave_group_call(chat_id)
        await message.edit("✅ VC chhod diya 🚪😈")
        
        # Queue clear
        global queue, current_playing
        queue.clear()
        current_playing = None
        
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("play") & filters.me)
async def play_music(client: Client, message: Message):
    """.play query - VC mein gaana bajao"""
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.edit("🤡 Usage: `.play song_name ya YouTube URL`")
            return
            
        query = args[1]
        await message.edit("🔍 Dhoond raha hoon... 🕵️")
        
        # URL get karo
        url = await get_audio_url(query)
        if not url:
            await message.edit("❌ Kuch nahi mila! Correct query daal 😡")
            return
            
        # Stream URL get karo
        stream_url = await get_stream_url(url)
        if not stream_url:
            await message.edit("❌ Stream nahi mila! Kuch aur try kar 😭")
            return
        
        # Current playing check
        global current_playing, queue
        
        if current_playing is None:
            # Play karo
            await call.change_stream(
                message.chat.id,
                AudioPiped(stream_url)
            )
            current_playing = query
            await message.edit(f"▶️ **Ab baja raha hoon:** `{query}`\n🎵 CHUMT KA GANA 😈🔥")
        else:
            # Queue mein daalo
            queue.append({
                'query': query,
                'url': url,
                'stream_url': stream_url
            })
            await message.edit(f"⏳ Queue mein daal diya: `{query}`\nPosition: `{len(queue)}` 🎶")
            
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}` 💀")

@app.on_message(filters.command("show") & filters.me)
async def show_rc(client: Client, message: Message):
    """.show - Saare saved RC dikhao"""
    if not saved_rc:
        await message.edit("📭 Koi RC save nahi hai! `.play rc_name` karke save kar 😭")
        return
        
    text = "📋 **SAVED RC LIST**\n"
    text += "═══*\n"
    for i, (name, url) in enumerate(saved_rc.items(), 1):
        text += f"{i}. `{name}` → {url[:50]}...\n"
    
    await message.edit(text)

@app.on_message(filters.command("addrc") & filters.me)
async def add_rc(client: Client, message: Message):
    """.addrc rc_name url - RC save karo"""
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.edit("🤡 Usage: `.addrc rc_name YouTube_URL`")
            return
            
        rc_name = args[1]
        url = args[2]
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            await message.edit("❌ Sahi URL daal! YouTube link daal 😡")
            return
            
        saved_rc[rc_name] = url
        save_rc()
        
        await message.edit(f"✅ RC `{rc_name}` save kar diya! Ab `.play {rc_name}` se baja 😈")
        
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("delrc") & filters.me)
async def del_rc(client: Client, message: Message):
    """.delrc rc_name - RC delete karo"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.edit("🤡 Usage: `.delrc rc_name`")
            return
            
        rc_name = args[1]
        if rc_name in saved_rc:
            del saved_rc[rc_name]
            save_rc()
            await message.edit(f"✅ RC `{rc_name}` delete kar diya! 🗑️")
        else:
            await message.edit(f"❌ RC `{rc_name}` exist nahi karta! `.show` dekh 😡")
            
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("skip") & filters.me)
async def skip_song(client: Client, message: Message):
    """.skip - Next song chalao queue se"""
    global queue, current_playing
    
    if not queue:
        await message.edit("📭 Queue khaali hai! Pehle kuch daal 😭")
        return
        
    next_song = queue.pop(0)
    current_playing = next_song['query']
    
    try:
        await call.change_stream(
            message.chat.id,
            AudioPiped(next_song['stream_url'])
        )
        await message.edit(f"⏭️ **Skip!** Ab baja raha hoon: `{next_song['query']}`\nQueue mein `{len(queue)}` songs 😈")
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("pause") & filters.me)
async def pause_vc(client: Client, message: Message):
    """.pause - VC pause karo"""
    try:
        await call.pause_stream(message.chat.id)
        await message.edit("⏸️ Pause kar diya! `.resume` se chalao 🥀")
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("resume") & filters.me)
async def resume_vc(client: Client, message: Message):
    """.resume - VC resume karo"""
    try:
        await call.resume_stream(message.chat.id)
        await message.edit("▶️ Resume kar diya! CHUMT KA GANA 😈🔥")
    except Exception as e:
        await message.edit(f"❌ Error: `{str(e)}`")

@app.on_message(filters.command("queue") & filters.me)
async def show_queue(client: Client, message: Message):
    """.queue - Queue dikhao"""
    if not queue:
        await message.edit("📭 Queue khaali hai!")
        return
        
    text = "📋 **QUEUE LIST**\n"
    text += "═══*\n"
    for i, song in enumerate(queue, 1):
        text += f"{i}. `{song['query']}`\n"
    
    await message.edit(text)

# ============= RUN (FIXED) =============
if __name__ == "__main__":
    print("🔥 OGGY-VC-USERBOT STARTING...")
    print("😈 CHUMT KA PYASA ACTIVATED!")
    
    # PyTgCalls start
    call.start()
    
    # EVENT LOOP FIX KE SAATH RUN
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.start())
    loop.run_forever()