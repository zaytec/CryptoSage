import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._subscriptions: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        await websocket.accept()
        async with self._lock:
            self._subscriptions[channel].add(websocket)

    async def disconnect(self, websocket: WebSocket, channel: str) -> None:
        async with self._lock:
            self._subscriptions[channel].discard(websocket)
            if not self._subscriptions[channel]:
                self._subscriptions.pop(channel, None)

    async def broadcast(self, channel: str, message: dict) -> None:
        async with self._lock:
            connections = list(self._subscriptions.get(channel, set()))
        stale: list[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                stale.append(connection)
        for connection in stale:
            await self.disconnect(connection, channel)

    @property
    def connection_count(self) -> int:
        return sum(map(len, self._subscriptions.values()))
