import time
import random

from ..messages.message import PeerMessage
from ..messages.message import ClientMessage
from ..log.log import Log

import asyncio
import logging

logger = logging.getLogger(__name__)

class ClientNode:
    def __init__(self, rank, cluster=[], timeout=5):
        self.name = str(rank)
        self.rank = rank

        self.log = []

        self.transport = None

        self.leader_rank = None

        self.cluster = cluster
        self.timeout = timeout
        self.next_timeout = self._get_next_timeout()
        self._timer = None
        self._start_timeout()
    
    def _get_next_timeout(self):
        # randomized timeouts
        return random.randrange(self.timeout, 2 * self.timeout)

    def _start_timeout(self):
        if self._timer is not None:
            self._timer.cancel()

        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self._timeout_reached)
        
    def _timeout_reached(self):
        self._start_timeout() # Reset Timeout
        next_target = self.cluster[random.randrange(0, len(self.cluster))]
        logger.info(f'[{self.name}] reached timeout. Consulting {next_target} for leader informations')
        self.leader_rank = next_target
        self.send_entry()


    def on_server(self, message, sender):
        if message.type == PeerMessage.ServerHeartbeatMessageType:
            self.on_heartbeat()
        if message.type == PeerMessage.RedirectionMessageType:
            self.on_redirection(message, sender)
        if message.type == PeerMessage.ServerEntryResponseType:
            self.on_confirmation(message, sender)


    def on_heartbeat(self):
        self._start_timeout() # Reset Timeout


    def read_next_entry(self):
        res = [self.rank]
        return res

    def send_entry(self):
        entry = self.read_next_entry()
        message = ClientMessage(self.name,  self.leader_rank, {'entries': entry})
        self.transport.sendto(message, self.leader_rank)


    def on_redirection(self, message, sender):
        self._start_timeout() # Reset Timeout
        if message.data["leader_rank"] is not None : 
            logger.info(f'[{self.name}] Reconducted to leader {message.data["leader_rank"]}')
            self.leader_rank = int(message.data["leader_rank"])
            self.send_entry()

    def on_confirmation(self, message, sender):
        self._start_timeout() # Reset Timeout
        return
        self.log.append(self.rank)
        self.send_entry()