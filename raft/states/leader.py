from .state import State
from ..messages.message import HeartBeatMessage

import asyncio
import logging

logger = logging.getLogger(__name__)

class Leader(State):
    def __init__(self):
        self.timeout = 5
        self.next_timeout = self._get_next_timeout()
        self._timer = None


    def set_server(self, server):
        super().set_server(server)
        

    def heartbeat(self):
        if self._timer:
            self._timer.cancel()
        heartbeat = HeartBeatMessage(self._server.name, None, self._server.term, {})

        self._server.broadcast_message(heartbeat)
        logger.info(f'[{self._server.name}] broadcasting heartbeat.')

        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self.heartbeat)


    def on_heartbeat_response(self, message, sender):
        # Commit logs?
        logger.info(f'[{self._server.name}] received heartbeat response from {":".join(map(str, sender))}.')