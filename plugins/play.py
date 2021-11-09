import os
from os import path
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from callsmusic import callsmusic, queues
from callsmusic.callsmusic import client as USER
from helpers.admins import get_administrators
import requests
import aiohttp
import yt_dlp
from youtube_search import YoutubeSearch
import converter
from downloaders import youtube
from config import DURATION_LIMIT, aiohttpsession
from helpers.filters import command
from helpers.decorators import errors
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
import aiofiles
import ffmpeg
from PIL import Image, ImageFont, ImageDraw

downloads = os.path.realpath("downloads")

def transcode(filename):
    ffmpeg.input(filename).output("input.raw", format='s16le', acodec='pcm_s16le', ac=2, ar='48k').overwrite_output().run() 
    os.remove(filename)

# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 80)
    draw.text((12, 530), "Now Playing ...", (0, 0, 0), font=font)
    draw.text((12, 620), f"{title[:25]} ...", (0, 0, 0), font=font)
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")



@Client.on_message(command("play") 
                   & filters.group
                   & ~filters.edited 
                   & ~filters.forwarded
                   & ~filters.via_bot)
async def play(_, message: Message):
    ls_dir = os.listdir(downloads)
    
    if ls_dir:
        for file in os.listdir(downloads):
            os.remove(os.path.join(downloads, file))
 
    lel = await message.reply("𝚃𝚁𝚈 𝙾𝙽.....")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "𝙰𝙽𝙺𝙸𝚃"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "𝙿𝙰𝙷𝙻𝙴 𝙰𝙳𝙼𝙸𝙽 𝚈𝙾 𝙱𝙽𝙰 𝙳𝙾 𝚂𝙸𝚁")
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "𝙸 𝙰𝙼 𝙽𝙾𝚆 𝚁𝙴𝙰𝙳𝚈 𝚃𝙾 𝙵𝚄𝙲𝙺")

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"𝙱𝚂𝙳𝙺 𝙼𝙴𝚁𝙴 𝙱𝙵 𝙹𝙸 𝙺𝙾 𝙱𝚄𝙻𝙰𝙰 𝙿𝙰𝙷𝙻𝙴")
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"𝙼𝚈 𝙱𝙵 𝙽𝙾𝚃 𝙹𝙾𝙸𝙽 𝚃𝙷𝙸𝚂 𝙲𝙷𝙰𝚃....")
        return
    
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"**𝙱𝚂𝙳𝙺 𝙰𝚄𝙺𝙺𝙰𝚃 𝚂𝙴 𝙹𝚈𝙰𝙳𝙰️ {DURATION_LIMIT} 💞 𝙷𝙰𝙸**"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/1b607954321bf1338db77.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="𝕆𝕎ℕ𝔼ℝ",
                            url=f"https://t.me/xD_PAPAi")

                ]
            ]
        )
        
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)  
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]       
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f'thumb{title}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")
            
            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
                
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝕆𝕎ℕ𝔼ℝ",
                            url=f"https://t.me/xD_PAPAi")

                    ]
                ]
            )
        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/1b607954321bf1338db77.jpg"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                    [
                        [
                        InlineKeyboardButton(
                            text="𝕆𝕎ℕ𝔼ℝ",
                            url=f"https://t.me/xD_PAPAi")

                       ]
                    ]
                )
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"*𝙻𝙸𝙼𝙸𝚃𝙴 𝙼𝙴 𝚂𝙾𝙽𝙶 𝙱𝙰𝙹𝙰𝙾 𝙱𝙴 𝙱𝚂𝙳𝙺⚡️ {DURATION_LIMIT} 💞 Ɱɩɳʋʈɘ ...**")
             return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)     
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit("𝙼𝚄𝚂𝙸𝙲 𝙺𝙰 𝙽𝙰𝙼𝙴 𝙻𝙸𝙺𝙷𝙾 𝙱𝙴.....*")
        await lel.edit("**🔎 Sɘɑɤƈɦɩɳʛ ...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit("**🔄 Ƥɤøƈɘssɩɳʛ ...**")
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]       
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f'thumb{title}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(':')
            for i in range(len(dur_arr)-1, -1, -1):
                dur += (int(dur_arr[i]) * secmul)
                secmul *= 60
                
        except Exception as e:
            await lel.edit(
                "**𝙼𝚄𝚂𝙸𝙲 𝙷𝙸 𝙽𝙰𝙰 𝙼𝙸𝙻𝙰 𝙱𝙴 𝙱𝚂𝙳𝙺 ..**"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                             text="𝕆𝕎ℕ𝔼ℝ",
                            url=f"https://t.me/xD_PAPAi")

                    ]
                ]
            )
        
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"**𝙼𝚄𝚂𝙸𝙲 𝙻𝙸𝙼𝙸𝚃𝙴 𝙼𝙴 𝙱𝙰𝙹𝙰𝙾 𝙱𝙴 𝚁𝙰𝙼𝙳𝙸𝙸⚡️ {DURATION_LIMIT} ...**")
             return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)  
        file_path = await converter.convert(youtube.download(url))
  
    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
        photo="final.png", 
        caption="**💥 𝚆𝙰𝙸𝚃𝙸𝙽𝙶 𝙱𝙴...**".format(position),
        reply_markup=keyboard)
        os.remove("final.png")
        return await lel.delete()
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
        photo="final.png",
        reply_markup=keyboard,
        caption="**𝙰𝙱𝙱 𝙼𝙰𝙹𝙹𝙴 𝙻𝙾 𝙱𝙰𝚂𝙺.**".format(), )
        os.remove("final.png")
        return await lel.delete()
