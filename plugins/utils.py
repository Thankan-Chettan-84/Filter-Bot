import re, os
from datetime import datetime
from typing import List, Union
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, Message

# Regex pattern for detecting buttons in messages
BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

def get_file_id(msg: Message):
    """Extracts file ID from a media message."""
    if msg.media:
        for message_type in (
            "photo", "animation", "audio", "document",
            "video", "video_note", "voice", "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def split_quotes(text: str) -> List:
    """Splits text while handling quoted arguments."""
    if any(text.startswith(char) for char in START_CHAR):
        counter = 1  # Ignore first char (which is a quote)
        while counter < len(text):
            if text[counter] == "\\":
                counter += 1
            elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
                break
            counter += 1
        else:
            return text.split(None, 1)

        key = remove_escapes(text[1:counter].strip())
        rest = text[counter + 1:].strip()
        return [key, rest] if key else [text[0] + text[0], rest]
    else:
        return text.split(None, 1)

def parser(text, keyword):
    """Parses text for buttons and alerts."""
    if "buttonalert" in text:
        text = text.replace("\n", "\\n").replace("\t", "\\t")
    
    buttons, alerts = [], []
    note_data, prev, i = "", 0, 0

    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)

            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2), callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2), callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                alerts.append(match.group(4))
                i += 1
            else:
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2), url=match.group(4).replace(" ", "")
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2), url=match.group(4).replace(" ", "")
                    )])
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    return note_data, buttons, alerts if alerts else None

def remove_escapes(text: str) -> str:
    """Removes escape characters from text."""
    res, is_escaped = "", False
    for char in text:
        if is_escaped:
            res += char
            is_escaped = False
        elif char == "\\":
            is_escaped = True
        else:
            res += char
    return res

def extract_user(message: Message) -> Union[int, str]:
    """Extracts user ID and first name from a message."""
    if message.reply_to_message:
        return message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name

    if len(message.command) > 1:
        user_input = message.command[1]
        try:
            return int(user_input), user_input  # ID extracted directly
        except ValueError:
            return user_input, user_input  # Return username or invalid ID

    return message.from_user.id, message.from_user.first_name

def last_online(from_user):
    """Returns the last online status of a user."""
    if from_user.is_bot:
        return "🤖 Bot :("
    status_map = {
        enums.UserStatus.RECENTLY: "Recently",
        enums.UserStatus.LAST_WEEK: "Within the last week",
        enums.UserStatus.LAST_MONTH: "Within the last month",
        enums.UserStatus.LONG_AGO: "A long time ago :(",
        enums.UserStatus.ONLINE: "Currently Online",
    }
    if from_user.status in status_map:
        return status_map[from_user.status]
    elif from_user.status == enums.UserStatus.OFFLINE:
        return from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S") if from_user.last_online_date else "Unknown last seen"
    return "Status Unknown"
