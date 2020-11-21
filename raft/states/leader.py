from .state import State
from ..messages.message import PeerMessage

import asyncio
import logging

logger = logging.getLogger(__name__)

class Leader(State):
    def __init__(self, timeout=2):
        self.timeout = timeout
        self.next_timeout = self._get_next_timeout()
        self._timer = None
        self.client_list = []
        self.max_log_size = 10

    def setup(self):
        self._server.leader_rank = self._server.rank
        self.nextIndex = {rank : self._server.log.last_log_index() + 1 for rank in self._server.cluster}
        self.matchIndex = {rank : 0 for rank in self._server.cluster}

    def set_server(self, server):
        super().set_server(server)


    def _start_timeout(self):
        if self._timer is not None:
            self._timer.cancel()
        
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self.send_append_entries())
    
        
    def send_client_heartbeat(self):
        for client in self.client_list:
            message = PeerMessage.ServerHeartbeatMessage(self._server.rank, client, {})
            self._server.send_message(message, client)
        if len(self.client_list):
            logger.info(f'[{self._server.currentTerm}][{self._server.name}] sending clients heartbeat.')



    def send_append_entries(self):
        self.send_client_heartbeat()
        for rank in self._server.cluster:
            if rank == self._server.rank:
                continue
            entries = []
            if self._server.log.next_index() >= self.nextIndex[rank]:
                entries = self._server.log.entry_from_index(self.nextIndex[rank])
                #logger.info(f'[{self._server.currentTerm}][{self._server.name}] broadcasted entries {entries}.')

            data = {'term' : self._server.currentTerm,
                    'leaderId':self._server.rank,
                    'prevLogIndex' : self.nextIndex[rank] - 1,
                    'prevLogTerm' : self._server.log.term_at_index(self.nextIndex[rank] - 1),
                    'entries' : entries,
                    'leaderCommit' : self._server.commitIndex}

            request = PeerMessage.AppendEntryMessage(self._server.rank, rank, data)
            self._server.send_message(request, rank)

    
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] broadcasted entries.')
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self.send_append_entries)


    def on_append_entries_response(self, message, sender):
        if message.data['success']:
            self.matchIndex[sender] = message.data['matchIndex']
            self.nextIndex[sender] += 1

            #check if we can commit last log

            nb_commit = 0
            for rank in self._server.cluster:
                if self.nextIndex[rank] > self._server.commitIndex:
                    nb_commit += 1
                
                if nb_commit > (len(self._server.cluster) - 1) // 2:
                    # commit log
                    logger.info(f'[{self._server.currentTerm}][{self._server.name}] Leader committed.')
                    log = self._server.log.entry_from_index(self._server.commitIndex)
                    self._server.commitIndex += 1
                    self._server.log.commit(self._server.commitIndex - 1, self._server.commitIndex)

                    # notify client
                    if log == []:
                        logger.info(f'[{self._server.currentTerm}][{self._server.name}]  WTF {self._server.commitIndex} {len(self._server.log.log)}.')

                    message = PeerMessage.ServerEntryResponse(self._server.rank, log[0].client_rank, {'success' : True})
                    self._server.send_message(message, log[0].client_rank)
                    return

        else:       
            self.nextIndex[sender] = max(0, self.nextIndex[sender] - 1)
        

    def on_client_message(self, message, sender):
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] request leader log replication from {str(sender)}')
        self._server.log.append_client_entries(message.data["entries"], self._server.currentTerm, sender)
        if not sender in self.client_list:
            self.client_list.append(sender)
        self.send_append_entries()
        