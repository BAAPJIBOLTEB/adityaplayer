# https://t.me/legendaditya

from helpers.filters import command
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(command("start") & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
    await message.reply_photo(
        photo=f"https://telegra.ph/file/1b607954321bf1338db77.jpg",
        caption=f"""
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💥 Ʌɗɗ Ɱɘ ʈø Yøʋɤ Ƈɦɑʈ 💞", url=f"https://t.me/adityaxbot?startgroup=true")
                ]
                
           ]
        ),
    )
    