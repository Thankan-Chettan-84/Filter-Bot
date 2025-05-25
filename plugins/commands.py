from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from .database import db
from config import *

START_TXT = """
{mention},

𝖨'𝗆 𝖺 𝗉𝗈𝗐𝖾𝗋𝖿𝗎𝗅 𝖨𝗇𝗅𝗂𝗇𝖾 𝖿𝗂𝗅𝗍𝖾𝗋 𝖻𝗈𝗍 𝗐𝗂𝗍𝗁 𝗅𝗂𝗆𝗂𝗍𝗅𝖾𝗌𝗌 𝖼𝖺𝗉𝖺𝖻𝗂𝗅𝗂𝗍𝗂𝖾𝗌!

𝖲𝖾𝗍 𝖿𝗂𝗅𝗍𝖾𝗋𝗌 𝖾𝖿𝖿𝗈𝗋𝗍𝗅𝖾𝗌𝗌𝗅𝗒 𝖺𝗇𝖽 𝗆𝖺𝗇𝖺𝗀𝖾 𝗋𝖾𝗌𝗉𝗈𝗇𝗌𝖾𝗌 𝗅𝗂𝗄𝖾 𝖺 𝗉𝗋𝗈.

<b><blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : <a href='https://telegram.me/CallOwnerBot'>ʀᴀʜᴜʟ</a></blockquote></b>
"""

HELP_TXT = """
𝖬𝖺𝗄𝖾 𝗆𝖾 𝖺𝗇 𝖺𝖽𝗆𝗂𝗇 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 𝗍𝗈 𝖾𝗇𝖺𝖻𝗅𝖾 𝖿𝗂𝗅𝗍𝖾𝗋𝗂𝗇𝗀 𝖿𝖾𝖺𝗍𝗎𝗋𝖾𝗌!

<b>𝖥𝗂𝗅𝗍𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:</b>
• <code>/𝖺𝖽𝖽 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 𝗋𝖾𝗌𝗉𝗈𝗇𝗌𝖾</code> - 𝖲𝖾𝗍 𝖺 𝗋𝖾𝗉𝗅𝗒 𝖿𝗈𝗋 𝖺 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝗐𝗈𝗋𝖽.
• <code>/𝖽𝖾𝗅 𝗄𝖾𝗒𝗐𝗈𝗋𝖽</code> - 𝖱𝖾𝗆𝗈𝗏𝖾 𝖺 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖿𝗂𝗅𝗍𝖾𝗋.
• <code>/𝖿𝗂𝗅𝗍𝖾𝗋𝗌</code> - 𝖲𝗁𝗈𝗐 𝖺𝗅𝗅 𝖺𝖼𝗍𝗂𝗏𝖾 𝖿𝗂𝗅𝗍𝖾𝗋𝗌.

<b>𝖢𝗈𝗇𝗇𝖾𝖼𝗍𝗂𝗈𝗇 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:</b>
• <code>/𝖼𝗈𝗇𝗇𝖾𝖼𝗍 𝗀𝗋𝗈𝗎𝗉𝗂𝖽</code> - 𝖫𝗂𝗇𝗄 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 𝗍𝗈 𝗆𝗒 𝖯𝖬. 𝖴𝗌𝖾 <code>/𝖼𝗈𝗇𝗇𝖾𝖼𝗍</code> 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌 𝖽𝗂𝗋𝖾𝖼𝗍𝗅𝗒.
• <code>/𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝗂𝗈𝗇𝗌</code> - 𝖬𝖺𝗇𝖺𝗀𝖾 𝗅𝗂𝗇𝗄𝖾𝖽 𝗀𝗋𝗈𝗎𝗉𝗌.
• <code>/𝖽𝗂𝗌𝖼𝗈𝗇𝗇𝖾𝖼𝗍</code> - 𝖱𝖾𝗆𝗈𝗏𝖾 𝗍𝗁𝖾 𝖺𝖼𝗍𝗂𝗏𝖾 𝖼𝗈𝗇𝗇𝖾𝖼𝗍𝗂𝗈𝗇.

<b>𝖮𝗍𝗁𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:</b>
• <code>/𝗂𝖽</code> - 𝖦𝖾𝗍 𝗎𝗌𝖾𝗋 𝗈𝗋 𝗀𝗋𝗈𝗎𝗉 𝖨𝖣.
• <code>/𝗂𝗇𝖿𝗈 𝗎𝗌𝖾𝗋𝗂𝖽</code> - 𝖦𝖾𝗍 𝗎𝗌𝖾𝗋 𝖽𝖾𝗍𝖺𝗂𝗅𝗌.

<b>𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:</b>
🔘 𝖡𝗎𝗍𝗍𝗈𝗇: <code>[𝖤𝗑𝖺𝗆𝗉𝗅𝖾] (buttonurl:https://telegram.me/TechifyBots)</code>
🔗 𝖫𝗂𝗇𝗄: <code>[𝖤𝗑𝖺𝗆𝗉𝗅𝖾] (https://telegram.me/TechifyBots)</code>

<b>𝖨𝖿 𝗒𝗈𝗎 𝗌𝗍𝗂𝗅𝗅 𝖿𝖺𝖼𝖾 𝖺𝗇𝗒 𝗂𝗌𝗌𝗎𝖾 𝗍𝗁𝖾𝗇 𝖼𝗈𝗇𝗍𝖺𝖼𝗍 @TechifySupport</b>
"""

@Client.on_message(filters.private & filters.command("start"))
async def startCMD(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.first_name, message.from_user.id)
        await client.send_message(
            chat_id=LOG_CHANNEL, 
            text=f"**#New\n\n👤 {message.from_user.mention}**\n\nID - `{message.from_user.id}`"
        )
    keyboard = [[InlineKeyboardButton('ʜᴇʟᴘ ᴄᴇɴᴛᴇʀ', callback_data='start')]]
    await message.reply_text(
        text=START_TXT.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_message(filters.private & filters.command("help"))
async def helpCMD(client: Client, message: Message):
    keyboard = [[InlineKeyboardButton('✗ ᴄʟᴏsᴇ ✗', callback_data='close_data')]]
    await message.reply_text(
        text=HELP_TXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )
