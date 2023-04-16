import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL = "gpt-3.5-turbo"
DATA_SOURCE_NAME = os.getenv("DATA_SOURCE_NAME")
