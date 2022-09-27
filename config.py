import os

from dotenv.main import load_dotenv

load_dotenv()

# Discord config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BOT_PREFIX = "?"
VERIFICATION_SPREADSHEET_ID = os.getenv('VERIFICATION_SPREADSHEET_ID')
TAB_DISCORD_RANGE = os.getenv('TAB_DISCORD_RANGE')
