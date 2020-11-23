from .state import State
from ..messages.message import PeerMessage
from ..log.log import Log

import asyncio
import logging

logger = logging.getLogger(__name__)

class Follower(State):
    def __init__(self, timeout):
        self.timeout = timeout

        self.next_timeout = self._get_next_timeout()
        
        self.votedFor = None
        self.lastVoteTerm = 0
        self._timer = None
        
        self._start_timeout()

    def _start_timeout(self):
        if self._timer is not None:
            self._timer.cancel()
        
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self._timeout_reached)
    
    def _timeout_reached(self):
        if not self._server.is_running:
            self._start_timeout() # Reset Timeout
            return
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] reached timeout.')
        self._timer.cancel()
        self._server.change_state_to_candidate()

    def on_append_entries_request(self, message, sender):
        self.votedFor = None
        term_condition = message.data['term'] >= self._server.currentTerm
        if term_condition:
            self._start_timeout() # Reset Timeout


        prev_log_condition = (message.data['prevLogTerm'] < 0
                              or (message.data["prevLogIndex"] < len(self._server.log.log)
                              and  self._server.log.term_at_index(message.data["prevLogIndex"]) ==
                              message.data['prevLogTerm']))

        success = term_condition and prev_log_condition

        if success:
            self._server.leader_rank = message.data['leaderId']
            self._server.log.insert_entries(message.data['entries'], message.data['prevLogIndex'] + 1)
            prev_commit = self._server.commitIndex
            if message.data['leaderCommit'] > self._server.commitIndex:
                self._server.commitIndex = min(message.data['leaderCommit'], len(self._server.log.log))
                logger.info(f'[{self._server.currentTerm}][{self._server.name}] new commitIndex {str(self._server.commitIndex)}.')
            self._server.log.commit(prev_commit, self._server.commitIndex)

        prevLogIndex = message.data["prevLogIndex"]
        term = message.data["prevLogTerm"]
        if message.data['entries'] != []:
            logger.info(f'[{self._server.currentTerm}][{self._server.name}] received entry from {str(sender)} answering {success} prevlogindex: {prevLogIndex}, term {term} .')
            response = PeerMessage.AppendEntryResponse(self._server.rank, message.sender, 
                                                    {'term': self._server.currentTerm,
                                                      'matchIndex' : self._server.log.last_log_index(),
                                                      'success':success})
            self._server.send_message(response, sender)

    def on_vote_request(self, message, sender):
        """ Follower on vote request

        Condition for yes:
            - have not voted during the term
            - follower log is not longer or newer than candidate
            - have received an heart beat from a leader before the election time out
        """
        term_condition = message.data['term'] >= self._server.currentTerm

        index_condition = (message.data['lastLogTerm'] > self._server.log.last_log_term() or 
                           (message.data['lastLogTerm'] == self._server.log.last_log_term() and
                            message.data['lastLogIndex'] >= self._server.log.last_log_index()))
        not_voted = self.votedFor is None or message.data['term'] > self.lastVoteTerm

        vote_yes = index_condition and term_condition and not_voted

        logger.info(f'[{self._server.currentTerm}][{self._server.name}] requested vote from {str(sender)} - answering {vote_yes}.')
        
        if vote_yes:
            self.votedFor = message.sender
            self.lastVoteTerm = message.data['term']
            self._start_timeout()
        
        response = PeerMessage.VoteResponse(self._server.rank, message.sender, {'vote': vote_yes, 'term' : self._server.currentTerm})

        # send response
        self._server.send_message(response, sender)

    def on_client_message(self, message, sender):
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] request leader rank from {str(sender)} - answering {self._server.leader_rank}.')
        response = PeerMessage.RedirectionMessage(self._server.rank, message.sender, {'leader_rank':self._server.leader_rank})
        self._server.send_message(response, sender)

    def on_repl_start(self, message):
        self._start_timeout() # Reset Timeout
        self._server.is_running = True
    
    def on_repl_crash(self, message):
        self._start_timeout()
        self._server.is_running = False

    def on_repl_recover(self, message):
        self._start_timeout() # Reset Timeout
        self._server.is_running = True