import discord
import openai
import functools
import typing
import config
import database

openai.api_key = config.OPEN_AI_KEY
intents = discord.Intents.all()
client = discord.Client(intents=intents)


async def exec_non_asyc_func(
    func: typing.Callable, *args, **kwargs
) -> typing.Any:
    """
    長時間かかるメソッドを非同期で実行するための関数。
    通常のasync関数のawait呼び出しであってもx秒以上経過するとDiscordBotがクラッシュするので、回避用に使う。
    """
    func = functools.partial(func, *args, **kwargs)
    return await client.loop.run_in_executor(None, func)


def create_compilation(discord_message):
    """
    OpenAIのAPIを呼び出す
    """
    channel_id: str = str(discord_message.channel.id)
    message: str = discord_message.content
    messages = database.fetch_chat_history_top10(channel_id)
    if messages == None:
        messages = [{"role": "user", "content": message}]
    else:
        messages.append({"role": "user", "content": message})
    personality = database.fetch_personality(channel_id)
    if personality != None:
        messages.insert(0, personality)
    completion = openai.ChatCompletion.create(
        model=config.AI_MODEL, messages=messages
    )
    ai_message = completion.choices[0]["message"]["content"]
    database.regist_chat_history(channel_id, message, ai_message)
    return ai_message


@client.event
async def on_ready():
    print("Bot起動")


is_waiting_personality_text: bool = False
temp_channel_id: str = ""


@client.event
async def on_message(discord_message):
    global is_waiting_personality_text
    global temp_channel_id
    channel_id: str = str(discord_message.channel.id)
    if discord_message.author.bot:
        return
    if is_waiting_personality_text and temp_channel_id == channel_id:
        database.regist_personality(channel_id, discord_message.content)
        is_waiting_personality_text = False
        await discord_message.channel.send("人格を変更しました。")
        return
    if discord_message.content == "!init_debug":
        await discord_message.channel.send("このチャンネルをAIとの会話に使用します。")
        database.regist_reply_channel_id(channel_id)
        return
    if discord_message.content == "!act":
        is_waiting_personality_text = True
        temp_channel_id = channel_id
        await discord_message.channel.send(
            """このチャンネルの回答の人格を変更します。
            人格を説明する文章をこのメッセージの直後に入力してください。"""
        )
        return
    if database.is_reply_channel_id(channel_id):
        await discord_message.channel.send(
            await exec_non_asyc_func(create_compilation, discord_message)
        )
        return


client.run(config.DISCORD_BOT_TOKEN)
