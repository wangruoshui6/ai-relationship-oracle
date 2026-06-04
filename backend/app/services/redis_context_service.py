"""Redis Context Service — Week 5.

Stores recent conversation messages for short-term context.
Uses in-memory dict as stub; swap to Redis when available.
"""
from collections import OrderedDict
from collections.abc import Generator


class RedisContextService:
    def __init__(self, max_messages: int = 20) -> None:
        self._store: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
        self.max_messages = max_messages

    def append(self, conversation_id: str, role: str, content: str) -> None:
        if conversation_id not in self._store:
            self._store[conversation_id] = []
        self._store[conversation_id].append({"role": role, "content": content})
        if len(self._store[conversation_id]) > self.max_messages:
            self._store[conversation_id] = self._store[conversation_id][-self.max_messages:]

    def get_context(self, conversation_id: str) -> list[dict[str, str]]:
        return self._store.get(conversation_id, [])[:]

    def clear(self, conversation_id: str) -> None:
        self._store.pop(conversation_id, None)


# 全局单例
redis_context = RedisContextService()
