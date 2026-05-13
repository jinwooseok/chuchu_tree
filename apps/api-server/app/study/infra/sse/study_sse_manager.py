import asyncio


class StudySSEManager:
    def __init__(self):
        # study_id → [(user_account_id, Queue)]
        self._queues: dict[int, list[tuple[int, asyncio.Queue]]] = {}

    def connect(self, study_id: int, user_account_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues.setdefault(study_id, []).append((user_account_id, q))
        return q

    def disconnect(self, study_id: int, user_account_id: int, q: asyncio.Queue) -> None:
        queues = self._queues.get(study_id, [])
        if (user_account_id, q) in queues:
            queues.remove((user_account_id, q))

    async def notify(
        self,
        study_id: int,
        event_type: str,
        payload: dict,
        exclude_user_account_id: int | None = None,
    ) -> None:
        data = {"eventType": event_type, "data": payload}
        for uid, q in self._queues.get(study_id, []):
            if uid != exclude_user_account_id:
                await q.put(data)
