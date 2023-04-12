import discord
import openai
import logging
import time
import datetime
import functools
import typing
from chatting import ChatHistory
import config
from managing import ChatChannelIdManager
from typing import Optional, TypedDict, Dict, List

logging.basicConfig(encoding="utf-8", level=logging.INFO)
openai.api_key = config.OPEN_AI_KEY

intents = discord.Intents.all()
client = discord.Client(intents=intents)
manager = ChatChannelIdManager()
AI_CHAT_CHANNEL_IDS = List[str]


def exec_per_minute():
    """
    1分間隔で定期実行
    """
    while True:
        global AI_CHAT_CHANNEL_IDS
        now = datetime.datetime.now()
        after_minute = now.second + now.microsecond / 1_000_000
        if after_minute:
            time.sleep(60 - after_minute)
        manager.update_json_channel_id()
        AI_CHAT_CHANNEL_IDS = manager.get_channel_ids()


async def exec_non_asyc_func(
    func: typing.Callable, *args, **kwargs
) -> typing.Any:
    """
    長時間かかるメソッドを非同期で実行するための関数。
    通常のasync関数のawait呼び出しであってもx秒以上経過するとDiscordBotがクラッシュするので、回避用に使う。
    """
    func = functools.partial(func, *args, **kwargs)
    return await client.loop.run_in_executor(None, func)


chat_history = ChatHistory()


def create_compilation(discord_message):
    """
    OpenAIのAPIを呼び出す
    """
    channel_id: str = str(discord_message.channel.id)
    message: str = discord_message.content
    messages = chat_history.get_history(channel_id)
    if messages == None:
        messages = [{"role": "user", "content": message}]
    else:
        messages.append({"role": "user", "content": message})
    completion = openai.ChatCompletion.create(
        model=config.AI_MODEL, messages=messages
    )
    ai_message = completion.choices[0]["message"]["content"]
    chat_history.add_message(
        channel_id=channel_id, role="assistant", message=ai_message
    )
    return ai_message


@client.event
async def on_ready():
    global AI_CHAT_CHANNEL_IDS
    logging.info("Bot起動")
    AI_CHAT_CHANNEL_IDS = manager.get_channel_ids()
    await exec_non_asyc_func(exec_per_minute)


@client.event
async def on_message(discord_message):
    channel_id: str = str(discord_message.channel.id)
    if discord_message.author.bot:
        return
    if discord_message.content == "!init":
        await discord_message.channel.send("このチャンネルをAIとの会話に使用します。")
        manager.save_channel_id(channel_id)
        return
    if channel_id in AI_CHAT_CHANNEL_IDS:
        await discord_message.channel.send(
            await exec_non_asyc_func(create_compilation, discord_message)
        )


client.run(config.DISCORD_BOT_TOKEN)
