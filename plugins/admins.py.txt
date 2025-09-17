import asyncio
import time
import datetime
import os
import aiofiles
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from config import ADMINS
from .database import db

async def send_msg(client: Client, user_id: int, message: Message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        wait_time = e.value
        if wait_time > 600:  # Stop retrying if flood wait is too long
            return 500, f"{user_id} : FloodWait too long ({wait_time}s)\n"
        await asyncio.sleep(wait_time)
        return await send_msg(client, user_id, message)
    except (InputUserDeactivated, UserIsBlocked):
        return 400, f"{user_id} : User Deactivated/Blocked\n"
    except Exception as e:
        return 500, f"{user_id} : {str(e)}\n"

@Client.on_message(filters.private & filters.command("broadcast") & filters.reply)
async def broadcast(client: Client, message: Message):
    if str(message.from_user.id) not in ADMINS:  # ✅ Compare as strings
        return await message.reply_text("🚫 You are not authorized to use this command.")

    broadcast_msg = message.reply_to_message
    all_users = await db.get_all_users()  # ✅ Now returns a list

    out = await message.reply_text("📢 **Broadcast Started!**")
    start_time = time.time()
    total_users = len(all_users)  # ✅ Get count from list

    done, failed, success = 0, 0, 0

    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        for user in all_users:  # ✅ Now using a normal for loop
            user_id = int(user['id'])
            sts, msg = await send_msg(client, user_id, broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            done += 1

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await out.delete()

    if failed == 0:
        await message.reply_text(
            f"✅ **Broadcast Completed in** `{completed_in}`\n\n"
            f"👥 **Total Users:** {total_users}\n"
            f"✅ **Success:** {success}\n"
            f"❌ **Failed:** {failed}",
            quote=True
        )
    else:
        await message.reply_document(
            document='broadcast.txt',
            caption=f"📢 **Broadcast Completed in** `{completed_in}`\n\n"
                    f"👥 **Total Users:** {total_users}\n"
                    f"✅ **Success:** {success}\n"
                    f"❌ **Failed:** {failed}"
        )

    os.remove('broadcast.txt')

@Client.on_message(filters.private & filters.command("stats"))
async def bot_stats(client: Client, message: Message):
    if str(message.from_user.id) not in ADMINS:  # ✅ Compare as strings
        return await message.reply_text("🚫 You are not authorized to use this command.")

    users = await db.total_users_count()
    await message.reply_text(
        f"👤 **Total Users:** {users}\n",
        quote=True
    )
