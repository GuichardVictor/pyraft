from .state import State
from .leader import Leader
from ..messages.message import VoteMessage

import logging

logger = logging.getLogger(__name__)

class Candidate(State):
    def __init__(self):
        self.voters = []
        self.last_vote = None

    def on_vote_request(self, message, sender):
        pass


    def on_vote_received(self, message, sender):
        """ Candidate on vote received

        Condition for becoming a leader:
            - candidate received the majority of votes
        """
        # Ensure there is no duplicate
        
        logger.info(f'[{self._server.name}] received vote from {":".join(map(str, sender))}: [{message.data["vote"]}].')
        if message.sender not in self.voters and message.data['vote']:
            self.voters.append(message.sender)

            # Does the candidate got the majority of votes (-1 because candidate votes for himself)
            if len(self.voters) > (self._server.total_nodes - 1) // 2:
                
                # candidate becomes the leader
                logger.info(f'[{self._server.name}] has majority: becomes Leader.')
                
                self._server.change_state(Leader())


    def start_election(self):
        self._server.term += 1

        logger.info(f'[{self._server.name}] starting an election.')
        election_message = VoteMessage(sender=self._server.name, receiver=None, term=self._server.term, data={'log_size': self._server.log_size})
        # Send message
        self._server.send_message(election_message)

        self.last_vote = self._server.name