from typing import Optional, TypedDict, Dict, List
import config


class Chat(TypedDict):
    role: str
    content: str


class ChatHistory:
    def __init__(self) -> None:
        self._history: Dict[str, List[Chat]] = {}

    def add_message(self, channel_id: str, role: str, message: str) -> bool:
        if (
            not isinstance(channel_id, str)
            or not isinstance(role, str)
            or not isinstance(message, str)
        ):
            return False

        message_list = self._history.get(channel_id, [])
        message_list.append(Chat(role=role, content=message))
        if len(message_list) > config.MESSAGE_HISTORY_LIMIT:
            del message_list[:2]
        self._history[channel_id] = message_list
        return True

    def get_history(self, channel_id: str) -> Optional[List[Chat]]:
        if channel_id in self._history:
            return self._history[channel_id]
        else:
            None
