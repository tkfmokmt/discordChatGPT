import datetime
import json
import time
import typing
import config
from typing import Optional, TypedDict, Dict, List


class ChatChannelIdManager:
    def __init__(self):
        self.ai_chat_channel_ids = List[str]
        self.update_json_channel_id()

    def read_channel_id_json(self) -> typing.Any:
        """
        チャンネルIDを保存しているJSONを読み込む
        """
        with open(config.JSON_FILE_NAME, mode="r") as f:
            return json.load(f)

    def update_json_channel_id(self):
        """
        グローバルで保持しているチャンネルIDをJSONから読み込んだチャンネルIDで更新する。
        """
        data = self.read_channel_id_json()
        self.ai_chat_channel_ids = data[config.JSON_KEY_CHANNEL_ID]

    def save_channel_id(self, channel_id: str):
        """
        チャンネルIDをJSONとグローバルで保持しているチャンネルIDのリストに保存する。
        """
        data = self.read_channel_id_json()
        with open(config.JSON_FILE_NAME, mode="w") as f:
            channel_ids = data.get(config.JSON_KEY_CHANNEL_ID, [])
            if channel_id not in channel_ids:
                channel_ids.append(channel_id)
            data[config.JSON_KEY_CHANNEL_ID] = channel_ids
            json.dump(data, f, indent=2)
        self.ai_chat_channel_ids.append(channel_id)

    def get_channel_ids(self) -> typing.List:
        return self.ai_chat_channel_ids
