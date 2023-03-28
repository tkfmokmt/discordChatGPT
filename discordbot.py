import discord
import openai
import logging
import os

logging.basicConfig(encoding="utf-8", level=logging.INFO)
openai.api_key = os.getenv("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
client = discord.Client(intents=intents)


async def create_compilation(message):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": message}]
    )
    return completion.choices[0]["message"]["content"]


@client.event
async def on_ready():
    logging.info("Bot起動")


ai_chat_channel_ids = []


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == "!init":
        await message.channel.send("このチャンネルをAIとの会話に使用します。")
        logging.info(
            "テキストチャンネル登録 チャンネルID:[%s], チャンネル名:[%s]",
            message.channel.id,
            message.channel.name,
        )
        ai_chat_channel_ids.append(message.channel.id)
        return
    if message.channel.id in ai_chat_channel_ids:
        await message.channel.send(await create_compilation(message.content))


client.run(DISCORD_BOT_TOKEN)
