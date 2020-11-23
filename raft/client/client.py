import time
import random
import csv
import asyncio
import logging

from ..messages.message import PeerMessage, ClientMessage, ReplMessage
from ..log.log import Log

logger = logging.getLogger(__name__)

class ClientNode:
    ''' Client class.

    This class is made custom since not described in raft paper.
    Client reads all request at the beginning and sends them each
    time the leader confirms commit of previous log.

    Args:
        rank: client id
        cluster: list of server ids
        timeout: time before considering leader dead (ms). 
    '''
    def __init__(self, rank, cluster, timeout):
        self.name = str(rank)
        self.rank = rank

        # list of all requests to send
        self.log = []
        # current index in log
        self.cur_index = 0
        self.read_all_entries()

        self.transport = None
        self.has_started = False
        
        # initialize leader rank to None
        self.leader_rank = None
        self.cluster = cluster

        self.next_timeout = timeout / 1000
        self._timer = None
        self._start_timeout()

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
        filename = f'client_log_{self.name}.log'

        with open(filename, newline='') as f:
            self.log = [line.rstrip('\n') for line in f]

    def read_next_entry(self):
        return self.log[self.cur_index]

    def send_entry(self):
        if self.cur_index >= len(self.log):
            return

        entry = self.read_next_entry()
        message = ClientMessage(self.name,  self.leader_rank, {'entries': entry})
        self.transport.sendto(message, self.leader_rank)

    def on_redirection(self, message, sender):
        self._start_timeout() # Reset Timeout

        if message.data["leader_rank"] is None:
            return

        logger.info(f'[{self.name}] Reconducted to leader {message.data["leader_rank"]}')
        self.leader_rank = int(message.data["leader_rank"])
        self.send_entry()

    def on_confirmation(self, message, sender):
        self._start_timeout() # Reset Timeout

        if self.cur_index >= len(self.log):
            return

        self.cur_index += 1
        self.send_entry()