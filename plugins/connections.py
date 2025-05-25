import logging
import pyrogram
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .database import db
from config import ADMINS

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are an anonymous admin. Use `/connect <group_id>` in PM.")

    chat_type = message.chat.type
    group_id = None  # Initialize group_id

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
            group_id = int(group_id)  # Ensure group_id is an integer
        except ValueError:
            return await message.reply_text(
                "<b>Invalid Format!</b>\n\n"
                "Use: <code>/connect group_id</code>\n"
                "You can get the group ID by adding this bot to the group and using <code>/id</code>.",
                quote=True
            )

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and userid not in ADMINS:
            return await message.reply_text("You must be an admin in the group!", quote=True)

    except Exception as e:
        logger.error(f"Error checking user admin status: {e}")
        return await message.reply_text(
            "Invalid Group ID or I'm not in the group.\n\n"
            "Ensure I am added to the group and try again.",
            quote=True,
        )

    try:
        bot_status = await client.get_chat_member(group_id, "me")
        if bot_status.status == enums.ChatMemberStatus.ADMINISTRATOR:
            chat_info = await client.get_chat(group_id)
            addcon = await db.add_connection(str(group_id), str(userid))

            if addcon:
                await message.reply_text(
                    f"✅ Successfully connected to **{chat_info.title}**!\n"
                    "You can now manage your group from PM.",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        f"✅ Connected to **{chat_info.title}**!",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text("You're already connected to this chat!", quote=True)
        else:
            await message.reply_text("Please make me an admin in the group!", quote=True)

    except Exception as e:
        logger.exception("Error adding connection:", exc_info=True)
        await message.reply_text('⚠ Some error occurred! Try again later.', quote=True)


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are an anonymous admin. Use `/connect <group_id>` in PM.")

    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("Use /connections to view or disconnect from groups.", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and str(userid) not in ADMINS:
            return await message.reply_text("You must be an admin to disconnect this group.", quote=True)

        delcon = await db.delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("✅ Successfully disconnected from this chat.", quote=True)
        else:
            await message.reply_text("❌ This chat isn't connected! Use /connect to connect.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id

    group_ids = await db.all_connections(str(userid))
    if not group_ids:
        return await message.reply_text("❌ No active connections. Connect to a group first!", quote=True)

    buttons = []
    for group_id in group_ids:
        try:
            chat_info = await client.get_chat(int(group_id))
            title = chat_info.title
            is_active = await db.if_active(str(userid), str(group_id))
            status_text = " - ACTIVE" if is_active else ""
            buttons.append([InlineKeyboardButton(f"{title}{status_text}", callback_data=f"groupcb:{group_id}:{status_text}")])
        except Exception as e:
            logger.error(f"Error fetching group info: {e}")

    if buttons:
        await message.reply_text(
            "🔹 **Your Connected Groups:**\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text("❌ No active connections. Connect to a group first!", quote=True)
