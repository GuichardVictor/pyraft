from .state import State
from ..messages.message import VoteResponse, HeartBeatResponse
from .candidate import Candidate

import asyncio
import logging

logger = logging.getLogger(__name__)

class Follower(State):
    def __init__(self, timeout=5):
        self.timeout = timeout

        self.next_timeout = self._get_next_timeout()
        
        self.last_vote = None
        self._timer = None
        
        self._start_timeout()

    def _start_timeout(self):
        if self._timer is not None:
            self._timer.cancel()
        
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self._timeout_reached)
    
    def _timeout_reached(self):
        logger.info(f'[{self._server.name}] reached timeout.')
        self._timer.cancel()
        self._server.change_state(Candidate())

    def on_heartbeat(self, message, sender):
        self._start_timeout() # Reset Timeout
        self.last_vote = None
        
        logger.info(f'[{self._server.name}] received heartbeat from {":".join(map(str, sender))}.')

        response = HeartBeatResponse(self._server.name, sender, self._server.term, {})
        self._server.send_message(response, sender)

    def on_vote_request(self, message, sender):
        """ Follower on vote request

        Condition for yes:
            - have not voted during the term
            - follower log is not longer or newer than candidate
            - have received an heart beat from a leader before the election time out
        """

        vote_yes = self.last_vote is None
        
        logger.info(f'[{self._server.name}] requested vote from {":".join(map(str, sender))} - answering {vote_yes}.')
        
        if vote_yes:
            self.last_vote = message.sender
            self._start_timeout()
        
        response = VoteResponse(self._server.name, message.sender, message.term, {'vote': vote_yes})

        # send response
        self._server.send_message(response, sender)