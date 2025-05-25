import os
import logging
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from .utils import extract_user, last_online  # Import last_online from utils.py

# Logger Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command("id"))
async def showid(client, message):
    """Shows ID information for users, groups, and replied users."""
    chat_type = message.chat.type
    user_id = message.from_user.id if message.from_user else "Anonymous"

    response = f"<b>Your ID:</b> <code>{user_id}</code>\n"

    if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        chat_id = message.chat.id
        response = (
            f"<b>Chat ID:</b> <code>{chat_id}</code>\n"
            f"<b>Your ID:</b> <code>{user_id}</code>\n"
        )

    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user_id = message.reply_to_message.from_user.id
        response += f"<b>Replied User ID:</b> <code>{replied_user_id}</code>\n"

    await message.reply_text(response, quote=True)

@Client.on_message(filters.command("info"))
async def who_is(client, message):
    """Fetches detailed user information."""
    status_message = await message.reply_text("`Fetching user info...`")
    await status_message.edit("`Processing user info...`")

    from_user = None
    from_user_id, _ = extract_user(message)

    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(f"❌ Error: {error}")
        return

    if not from_user:
        await status_message.edit("❌ No valid user_id or message specified.")
        return

    # User Info Formatting
    message_out_str = (
        f"<b>➲ First Name:</b> {from_user.first_name}\n"
        f"<b>➲ Last Name:</b> {from_user.last_name or 'None'}\n"
        f"<b>➲ Telegram ID:</b> <code>{from_user.id}</code>\n"
        f"<b>➲ Username:</b> @{from_user.username if from_user.username else 'None'}\n"
        f"<b>➲ Data Centre:</b> <code>{from_user.dc_id or 'Unknown'}</code>\n"
        f"<b>➲ User Link:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"
        f"<b>➲ Last Seen:</b> {last_online(from_user)}\n"  # Added last online status
    )

    # If in a group, check if the user is a member
    if message.chat.type in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        try:
            chat_member = await message.chat.get_member(from_user.id)
            joined_date = (
                chat_member.joined_date or datetime.now()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += f"<b>➲ Joined this Chat on:</b> <code>{joined_date}</code>\n"
        except UserNotParticipant:
            message_out_str += "<b>➲ Not a member of this chat.</b>\n"

    # Fetch User Profile Photo
    chat_photo = from_user.photo
    buttons = [[InlineKeyboardButton('✗ ᴄʟᴏsᴇ ✗', callback_data='close_data')]]
    reply_markup = InlineKeyboardMarkup(buttons)

    if chat_photo:
        local_user_photo = await client.download_media(chat_photo.big_file_id)
        await message.reply_photo(
            photo=local_user_photo,
            caption=message_out_str,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
        os.remove(local_user_photo)
    else:
        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            quote=True,
            disable_notification=True
        )

    await status_message.delete()
