"""
設定値はそのうちJSONから読み込む
"""
import os

MESSAGE_HISTORY_LIMIT = 10
JSON_FILE_NAME = "channel_id.json"
JSON_KEY_CHANNEL_ID = "channel_id"
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL = "gpt-3.5-turbo"
