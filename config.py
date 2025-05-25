from os import environ

API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", ""))
DATABASE_URI = environ.get("DATABASE_URI", "")
DATABASE_NAME = environ.get("DATABASE_NAME", "")
ADMINS = set(str(x) for x in environ.get("ADMINS", "").split())
AUTO_DELETE = environ.get("AUTO_DELETE", "1") == "1"
AUTO_DELETE_SECOND = int(environ.get("AUTO_DELETE_SECOND", "300"))
