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

    async def notify(self, user_account_id: int, event_type: str, payload: dict) -> None:
        """SSE 이벤트 전송.

        Args:
            user_account_id: 수신자
            event_type: 이벤트 종류 (예: "NOTICE")
            payload: 이벤트 데이터
        """
        data = {"eventType": event_type, "data": payload}
        for q in self._queues.get(user_account_id, []):
            await q.put(data)
