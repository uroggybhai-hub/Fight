# OGGY-VC-USERBOT - TELEthon + PyTgCalls 😈🔥
# CHUMT KA PYASA - PEER ERROR FIXED

import asyncio
import os
import json
import subprocess
import sys
import traceback
from datetime import datetime

# ============ TELEthon IMPORTS ============
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import FloodWaitError

# ============ PyTgCalls IMPORTS ============
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality
from pytgcalls.types.input_stream import AudioPiped

import yt_dlp
from youtubesearchpython import VideosSearch

# ==================== CONFIG ====================
API_ID = 38712417
API_HASH = "4b583e8882508b7db133f8502b7b105f"
SESSION = "ELUMTER_COPY_userbot"
PLAYLIST_FILE = "playlist.json"

# 🔥 TERI USER ID
OWNER_ID = 8477195695

# ==================== INIT ====================
app = TelegramClient(SESSION, API_ID, API_HASH)
call = PyTgCalls(app)

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
        await app.send_file(chat_id, ffmpeg_process.stdout, voice_note=True)
    except Exception as e:
        print(f"Play error: {e}")

# ==================== COMMANDS ====================

@app.on(events.NewMessage(pattern=r'\.start'))
async def start_cmd(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!** Your ID: `{user_id}`")
            return
        
        await event.reply(
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
            "`.ping` - Check status\n"
            "`.debug` - Show debug info\n\n"
            f"👑 Owner ID: `{OWNER_ID}`\n"
            "😈 CHUMT KA PYASA ACTIVE!"
        )
    except Exception as e:
        print(f"Start error: {e}")

@app.on(events.NewMessage(pattern=r'\.debug'))
async def debug_cmd(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!** Your ID: `{user_id}`")
            return
        
        me = await app.get_me()
        await event.reply(
            f"🔍 **DEBUG INFO**\n\n"
            f"Your ID: `{user_id}`\n"
            f"Owner ID: `{OWNER_ID}`\n"
            f"Match: `{user_id == OWNER_ID}`\n"
            f"Bot ID: `{me.id}`\n"
            f"Bot Name: `{me.first_name}`\n"
            f"Queue: `{len(queue)}` songs\n"
            f"Current: `{current_playing}`\n"
            f"Saved RC: `{len(saved_rc)}`\n"
            f"FFmpeg: `{ffmpeg_process is not None}`\n"
            f"Python: `{sys.version}`"
        )
    except Exception as e:
        print(f"Debug error: {e}")
        await event.reply(f"❌ Error: `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.ping'))
async def ping_cmd(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        start = datetime.now()
        await event.reply("🏓 Pinging...")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        await event.reply(f"🏓 **Pong!** `{ms:.2f}ms`")
    except Exception as e:
        print(f"Ping error: {e}")

@app.on(events.NewMessage(pattern=r'\.joinvc (.+)'))
async def join_vc(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        chat_id = int(event.pattern_match.group(1))
        await event.reply(f"🔍 **Joining VC...** `{chat_id}`")
        
        try:
            await app(JoinChannelRequest(chat_id))
        except:
            try:
                await app(ImportChatInviteRequest(chat_id))
            except:
                pass
        
        await call.join_group_call(
            chat_id,
            AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"),
            AudioQuality.MEDIUM
        )
        
        await event.reply(f"✅ **VC Joined!** `{chat_id}` 😈")
    except Exception as e:
        print(f"Joinvc error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.leavevc'))
async def leave_vc(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        chat_id = event.chat_id
        stop_ffmpeg()
        global queue, current_playing
        queue.clear()
        current_playing = None
        
        await call.leave_group_call(chat_id)
        await event.reply(f"✅ **Left VC!** `{chat_id}` 🚪")
    except Exception as e:
        print(f"Leavevc error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        query = event.pattern_match.group(1)
        await event.reply(f"🔍 **Searching...** `{query}`")
        
        if query in saved_rc:
            url = saved_rc[query]
        else:
            url = await get_audio_url(query)
        
        if not url:
            await event.reply("❌ **No results found!**")
            return
        
        stream_url = get_stream_url(url)
        if not stream_url:
            await event.reply("❌ **Stream unavailable!**")
            return
        
        global current_playing, queue
        
        if current_playing is None:
            await event.reply(f"▶️ **Playing...** `{query}`")
            await play_audio(event.chat_id, stream_url)
            current_playing = query
            await event.reply(f"▶️ **Now Playing:** `{query}` 😈🔥")
        else:
            queue.append({'query': query, 'stream_url': stream_url})
            await event.reply(f"⏳ **Added to Queue:** `{query}` (Position: {len(queue)})")
    except Exception as e:
        print(f"Play error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.skip'))
async def skip_song(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        global queue, current_playing
        
        if not queue:
            await event.reply("📭 **Queue empty!**")
            return
        
        stop_ffmpeg()
        next_song = queue.pop(0)
        current_playing = next_song['query']
        
        await play_audio(event.chat_id, next_song['stream_url'])
        await event.reply(f"⏭️ **Now Playing:** `{next_song['query']}` (Queue: {len(queue)})")
    except Exception as e:
        print(f"Skip error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.stop'))
async def stop_music(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        stop_ffmpeg()
        global current_playing, queue
        current_playing = None
        queue.clear()
        await event.reply("⏹️ **Stopped!** 🛑")
    except Exception as e:
        print(f"Stop error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.queue'))
async def show_queue(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        if not queue:
            await event.reply("📭 **Queue is empty!**")
            return
        
        text = "📋 **QUEUE LIST**\n═══════\n"
        for i, song in enumerate(queue, 1):
            text += f"{i}. `{song['query']}`\n"
        await event.reply(text)
    except Exception as e:
        print(f"Queue error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.addrc (.+) (.+)'))
async def add_rc(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        name = event.pattern_match.group(1)
        url = event.pattern_match.group(2)
        saved_rc[name] = url
        save_rc()
        await event.reply(f"✅ **RC Saved:** `{name}`")
    except Exception as e:
        print(f"Addrc error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.show'))
async def show_rc(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        if not saved_rc:
            await event.reply("📭 **No saved RC!**")
            return
        
        text = "📋 **SAVED RC LIST**\n═══════\n"
        for i, (name, url) in enumerate(saved_rc.items(), 1):
            text += f"{i}. `{name}` → {url[:40]}...\n"
        await event.reply(text)
    except Exception as e:
        print(f"Show error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

@app.on(events.NewMessage(pattern=r'\.delrc (.+)'))
async def del_rc(event):
    try:
        user_id = event.sender_id
        if user_id != OWNER_ID:
            await event.reply(f"❌ **Owner only!**")
            return
        
        name = event.pattern_match.group(1)
        if name in saved_rc:
            del saved_rc[name]
            save_rc()
            await event.reply(f"✅ **RC Deleted:** `{name}`")
        else:
            await event.reply(f"❌ `{name}` not found!")
    except Exception as e:
        print(f"Delrc error: {e}")
        await event.reply(f"❌ **Error:** `{str(e)}`")

# ==================== UNKNOWN COMMAND ====================
@app.on(events.NewMessage)
async def catch_all(event):
    if event.text and event.text.startswith('.'):
        user_id = event.sender_id
        if user_id == OWNER_ID:
            await event.reply(
                f"❌ **Unknown command!**\n\n"
                f"Your command: `{event.text}`\n\n"
                f"Use `.start` to see all commands 😡"
            )

# ==================== RUN ====================
async def main():
    print("🔥 OGGY-VC-USERBOT STARTING...")
    print("😈 CHUMT KA PYASA ACTIVATED!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("🛡️ USING TELETHON - NO PEER ERRORS!")
    print("=" * 50)
    
    # Start client
    await app.start()
    me = await app.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username})")
    print(f"📱 Bot User ID: {me.id}")
    
    # Start PyTgCalls
    await call.start()
    print("✅ PyTgCalls started!")
    
    print("\n🎵 Bot is running!")
    print("📱 Send commands in PRIVATE chat or GROUP!")
    print("Commands: .start, .debug, .joinvc, .play, .skip, .stop, .queue, .addrc, .show, .delrc")
    
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
        traceback.print_exc()
        stop_ffmpeg()
