import asyncio


class NoticeSSEManager:
    def __init__(self):
        self._queues: dict[int, list[asyncio.Queue]] = {}

    def connect(self, user_account_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues.setdefault(user_account_id, []).append(q)
        return q

    def disconnect(self, user_account_id: int, q: asyncio.Queue) -> None:
        queues = self._queues.get(user_account_id, [])
        if q in queues:
            queues.remove(q)

    async def notify(self, user_account_id: int, data: dict) -> None:
        for q in self._queues.get(user_account_id, []):
            await q.put(data)
