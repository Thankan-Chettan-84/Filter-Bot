import ast
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from .database import db
from config import *
from .commands import START_TXT, HELP_TXT

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data_parts = query.data.split(":")
    try:
        if query.data == "close_data":
            await query.answer("ᴛʜᴀɴᴋs ꜰᴏʀ ᴄʟᴏsɪɴɢ ❤️", show_alert=True)
            await query.message.delete()

        elif query.data == "start":
            keyboard = [[InlineKeyboardButton('ʜᴇʟᴘ ᴄᴇɴᴛᴇʀ', callback_data="help")]]
            await query.message.edit_text(
                text=START_TXT.format(mention=query.from_user.mention),
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )

        elif query.data == "help":
            keyboard = [[
                InlineKeyboardButton('👨‍💻  ᴏᴡɴᴇʀ', url='https://telegram.me/CallOwnerBot'),
                InlineKeyboardButton('💥  ᴜᴘᴅᴀᴛᴇs', url='https://telegram.me/TechifyBots')
            ], [
                InlineKeyboardButton('ʜᴏᴍᴇ', callback_data="start")
            ]]
            await query.message.edit_text(
                text=HELP_TXT,
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )

        elif "groupcb" in query.data:
            await query.answer()
            group_id = data_parts[1]
            status = data_parts[2] if len(data_parts) > 2 else ""
            chat = await client.get_chat(int(group_id))
            title = chat.title
            button_label = "DISCONNECT" if status else "CONNECT"
            callback_data = "disconnect" if status else "connectcb"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(button_label, callback_data=f"{callback_data}:{group_id}"),
                 InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
                [InlineKeyboardButton("BACK", callback_data="backcb")]
            ])
            await query.message.edit_text(f"Group Name: **{title}**\nGroup ID: `{group_id}`",
                                          reply_markup=keyboard, parse_mode=enums.ParseMode.MARKDOWN)

        elif "connectcb" in query.data:
            await query.answer()
            group_id = data_parts[1]
            chat = await client.get_chat(int(group_id))
            title = chat.title
            if await db.make_active(str(query.from_user.id), str(group_id)):
                await query.message.edit_text(f"Connected to **{title}**", parse_mode=enums.ParseMode.MARKDOWN)
            else:
                await query.message.edit_text("An error occurred while connecting.", parse_mode=enums.ParseMode.MARKDOWN)

        elif "disconnect" in query.data:
            await query.answer()
            group_id = data_parts[1]
            chat = await client.get_chat(int(group_id))
            title = chat.title
            if await db.make_inactive(str(query.from_user.id)):
                await query.message.edit_text(f"Disconnected from **{title}**", parse_mode=enums.ParseMode.MARKDOWN)
            else:
                await query.message.edit_text("An error occurred while disconnecting.", parse_mode=enums.ParseMode.MARKDOWN)

        elif "deletecb" in query.data:
            await query.answer()
            group_id = data_parts[1]
            if await db.delete_connection(str(query.from_user.id), str(group_id)):
                await query.message.edit_text("Successfully deleted the connection.")
            else:
                await query.message.edit_text("An error occurred while deleting the connection.")

        elif query.data == "backcb":
            await query.answer()
            user_id = query.from_user.id
            group_ids = await db.all_connections(str(user_id))
            if not group_ids:
                await query.message.edit_text("No active connections! Connect to a group first.")
                return
            buttons = []
            for group_id in group_ids:
                try:
                    chat = await client.get_chat(int(group_id))
                    title = chat.title
                    is_active = await db.if_active(str(user_id), str(group_id))
                    active_status = " - ACTIVE" if is_active else ""
                    buttons.append([InlineKeyboardButton(f"{title}{active_status}", callback_data=f"groupcb:{group_id}:{active_status}")])
                except:
                    pass
            if buttons:
                await query.message.edit_text("Your connected groups:", reply_markup=InlineKeyboardMarkup(buttons))

        elif "alertmessage" in query.data:
            group_id = query.message.chat.id
            index, keyword = data_parts[1], data_parts[2]
            reply_text, btn, alerts, fileid = await db.find_filter(group_id, keyword)
            if alerts:
                alerts = ast.literal_eval(alerts)
                alert_text = alerts[int(index)].replace("\\n", "\n").replace("\\t", "\t")
                await query.answer(alert_text, show_alert=True)

    except Exception as e:
        await query.answer("An unexpected error occurred.", show_alert=True)
        print(f"Error in callback handler: {e}")
