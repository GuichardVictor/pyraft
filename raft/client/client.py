import time
import random
import csv

from ..messages.message import PeerMessage, ClientMessage, ReplMessage
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
        self.has_started = False
        self.leader_rank = None
        self.curIndex = 0

        self.cluster = cluster
        self.timeout = timeout
        self.next_timeout = self._get_next_timeout()
        self._timer = None
        self.read_all_entries()
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
        if not self.has_started:
            return
        next_target = self.cluster[random.randrange(0, len(self.cluster))]
        logger.info(f'[{self.name}] reached timeout. Consulting {next_target} for leader informations')
        self.leader_rank = next_target
        self.send_entry()

    def on_repl(self, message):                
        if message.type == ReplMessage.ReplStartMessageType:
            self._start_timeout() # Reset Timeout
            self.has_started = True
        elif message.type == ReplMessage.ReplStopMessageType:
            loop = asyncio.get_event_loop()
            
            for task in asyncio.all_tasks():
                task.cancel()
            loop.stop()
            raise asyncio.CancelledError()
        else:
            pass

    def on_server(self, message, sender):
        if message.type == PeerMessage.ServerHeartbeatMessageType:
            self.on_heartbeat()
        if message.type == PeerMessage.RedirectionMessageType:
            self.on_redirection(message, sender)
        if message.type == PeerMessage.ServerEntryResponseType:
            self.on_confirmation(message, sender)

    def on_heartbeat(self):
        self._start_timeout() # Reset Timeout


    def read_all_entries(self):
        filename = 'client_log_' + str(self.rank) + ".log"
        with open(filename, newline='') as csvfile:
            values = csv.reader(csvfile, delimiter='\n')
            for value in values:
                self.log.append(str(*value))
        print(self.log)

    def read_next_entry(self):
        res = self.log[self.curIndex]
        return res

    def send_entry(self):
        if self.curIndex >= len(self.log):
            return
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
        if self.curIndex >= len(self.log):
            return
        self.curIndex += 1
        self.send_entry()