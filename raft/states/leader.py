from .state import State
from ..messages.message import PeerMessage
import asyncio
import logging

logger = logging.getLogger(__name__)

class Leader(State):
    ''' Raft Leader class

    Python representation of the Leader state in raft paper

    Args:
        timeout: time interval between heartbeats
    '''

    def __init__(self, timeout):
        self.client_list = [] # list of client having pending entries

        self.next_timeout = timeout / 1000.0
        self._timer = None

    def setup(self):
        self._server.leader_rank = self._server.rank

        self.nextIndex = {rank : len(self._server.log.log) for rank in self._server.cluster} # cf raft paper
        self.matchIndex = {rank : 0 for rank in self._server.cluster} #cf raft paper

    def set_server(self, server):
        super().set_server(server)


    def _start_timeout(self):
        if self._timer is not None:
            self._timer.cancel()
        
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self.send_append_entries())
    
        
    def send_client_heartbeat(self):
        ''' Send heartbeat to clients '''
        for client in self.client_list:
            message = PeerMessage.ServerHeartbeatMessage(self._server.rank, client, {})
            self._server.send_message(message, client)

        if len(self.client_list):
            logger.info(f'[{self._server.currentTerm}][{self._server.name}] sending clients heartbeat.')

    def send_append_entries(self):
        ''' Send appendEntries to servers and heartbeat to clients:
        message contains:
            - index of previous log (different for each client, nextIndex -1)
            - term of previous log
            - logs from previous  to len(log) (limit is 100 log at a time) 
            - leader commit index for follower to update
        '''
        if not self._server.is_running:
            return
        self.send_client_heartbeat()
        for rank in self._server.cluster:
            if rank == self._server.rank:
                continue
            entries = []
            if len(self._server.log.log) > self.nextIndex[rank]:
                entries = self._server.log.entries_from_index(self.nextIndex[rank])
                logger.info(f'[{self._server.currentTerm}][{self._server.name}] sending entries {len(self._server.log.log)} vs {self.nextIndex[rank]}.')

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
        ''' Check if there is logs to commit or if sender has old logs
        If append entry was a success:
            - update servers information (next_index match_index) 
            - If majority of servers has already appended N entry (accepted) commits N next entries
        
        If append entry was not a success:
            - decrease next_index to send older log
        '''
        if message.data['success']:
            if self.nextIndex[sender] <= len(self._server.log.log) and message.data['matchIndex'] > self.matchIndex[sender]:
                self.matchIndex[sender] = message.data['matchIndex']
                self.nextIndex[sender] = self.matchIndex[sender] + 1

            #check if we can commit some logs
            nb_commit = [len(self._server.log.log) - self._server.commitIndex]
            for rank in self._server.cluster:
                if self.nextIndex[rank] > self._server.commitIndex:
                    nb_commit.append(self.nextIndex[rank] - self._server.commitIndex)

            # Finds prev_max_commit such as prev_max_commit has been appended by majority of servers
            prev_max_commit = 0
            while len(nb_commit) > len(self._server.cluster) // 2:
                prev_max_commit += 1
                nb_commit = list(map(lambda elt : elt - 1, nb_commit))
                nb_commit = list(filter(lambda elt: elt > 0, nb_commit))

            if prev_max_commit > 0:
                # find index with correct term 
                if self._server.log.term_at_index(self._server.commitIndex + (prev_max_commit - 1)) != self._server.currentTerm:
                    reel_max_commit = 0
                    for i in range(1, prev_max_commit + 1):
                        if self._server.log.term_at_index(self._server.commitIndex + (i - 1)) == self._server.currentTerm:
                            reel_max_commit = i
                    prev_max_commit = reel_max_commit

                logger.info(f'[{self._server.currentTerm}][{self._server.name}] Leader committing {str(prev_max_commit)} next entries.')
                for _ in range(prev_max_commit):
                    # commit log
                    log = self._server.log.entry_from_index(self._server.commitIndex)
                    self._server.log.commit(self._server.commitIndex, self._server.commitIndex + 1)
                    self._server.commitIndex += 1
                    # inform client
                    message = PeerMessage.ServerEntryResponse(self._server.rank, log[0].client_rank, {'success' : True})
                    self._server.send_message(message, log[0].client_rank)
        else:
            self.nextIndex[sender] = max(0, self.nextIndex[sender] - 1)

    def on_client_message(self, message, sender):
        ''' Appends entries sent by client '''
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] request leader log replication from {str(sender)}')
        self._server.log.append_client_entry(message.data["entries"], self._server.currentTerm, sender)
        if not sender in self.client_list:
            self.client_list.append(sender)

    def on_repl_recover(self, message):
        self._timer.cancel()
        self._server.is_running = True
        self._server.change_state_to_follower()
    
    def on_repl_crash(self, message):
        self._timer.cancel()
        self._server.is_running = False
        self._server.change_state_to_follower()