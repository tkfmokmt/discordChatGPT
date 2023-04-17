import config
import psycopg2
from typing import Dict, List
import config
from psycopg2.extras import DictCursor

DATA_SOURCE_NAME = config.DATA_SOURCE_NAME
# TODO: コネクションは毎回作成せずに、一度作成して使いまわすべき？
# その場合、close()はどうやって確実に実行する？


def get_connection():
    global DATA_SOURCE_NAME
    return psycopg2.connect(DATA_SOURCE_NAME)


def regist_reply_channel_id(channel_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reply_channel_ids(channel_id) VALUES(%s) ON CONFLICT DO NOTHING",
                (channel_id,),
            )
            conn.commit()


def delete_reply_channel_id(channel_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM reply_channel_ids WHERE channel_id = %s",
                (channel_id,),
            )
            conn.commit()
    delete_chat_history(channel_id)
    delete_ai_personality(channel_id)


def is_reply_channel_id(channel_id: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select count(*) from reply_channel_ids where channel_id = %s",
                (channel_id,),
            )
            if cur.fetchone()[0] > 0:
                return True
            else:
                return False


def regist_chat_history(
    channel_id: str, user_message: str, assistant_message: str
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_history(channel_id, role, content) VALUES (%s, %s, %s), (%s, %s, %s)",
                (
                    channel_id,
                    "user",
                    user_message,
                    channel_id,
                    "assistant",
                    assistant_message,
                ),
            )
            conn.commit()


def fetch_chat_history_top10(channel_id: str) -> List[Dict]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "SELECT role, content FROM chat_history WHERE channel_id = %s ORDER BY seq OFFSET 0 LIMIT 10",
                (channel_id,),
            )
            result = cur.fetchall()
            if len(result) == 0:
                return None
            retList = []
            for history in result:
                retList.append(
                    {"role": history["role"], "content": history["content"]}
                )
            return retList


def delete_chat_history(channel_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM chat_history WHERE channel_id = %s",
                (channel_id,),
            )
            conn.commit()


def regist_ai_personality(channel_id: str, personality_text: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ai_personalitys(channel_id, personality_text) VALUES(%s, %s) ON CONFLICT(channel_id) DO UPDATE SET personality_text = %s",
                (
                    channel_id,
                    personality_text,
                    personality_text,
                ),
            )
            conn.commit()
    # それまでの会話履歴が新しい人格の回答に影響するため
    delete_chat_history(channel_id)


def delete_ai_personality(channel_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ai_personalitys WHERE channel_id = %s",
                (channel_id,),
            )
            conn.commit()


def fetch_personality(channel_id: str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "SELECT personality_text FROM ai_personalitys WHERE channel_id = %s",
                (channel_id,),
            )
            result = cur.fetchall()
            if len(result) == 0:
                return None
            return {
                "role": "system",
                "content": result[0]["personality_text"],
            }
