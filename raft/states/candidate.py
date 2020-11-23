import asyncio
import logging

from .state import State
from ..messages.message import PeerMessage

logger = logging.getLogger(__name__)

class Candidate(State):
    ''' Raft Candidate class

    Python representation of the candidate state in raft paper

    Args:
        timeout: time before redoing election
    '''

    def __init__(self, timeout):
        self.last_vote = None
        self.timeout = timeout

    def _start_timeout(self):
        if self._timer is not None:
            self._timer.cancel()
        
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(self.next_timeout, self._timeout_reached)

    def _timeout_reached(self):
        if not self._server.is_running:
            self._start_timeout() # Reset Timeout
            return

        logger.info(f'[term:{self._server.currentTerm}][server_id:{self._server.name}] reached timeout.')
        self._timer.cancel()
        self.start_election()

    def on_vote_received(self, message, sender):
        # Ensure there is no duplicate
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] received vote from {str(sender)}: [{message.data["vote"]}].')
        if message.sender not in self.voters and message.data['vote']:
            self.voters.append(message.sender)

            # Does the candidate got the majority of votes (-1 because candidate votes for himself)
            if len(self.voters) > len(self._server.cluster) // 2:
                
                # candidate becomes the leader
                logger.info(f'[{self._server.currentTerm}][{self._server.name}] has majority: becomes Leader.')
                self._timer.cancel()
                self._server.change_state_to_leader()

    def start_election(self):
        self.last_vote = self._server.name
        self.voters = [self._server.rank] # vote for itself
        self._server.currentTerm += 1 # increase current term
        self._server.leader_rank = None # for client redirection

        self.next_timeout = self._get_next_timeout()
        self._timer = None
        self._start_timeout()

        logger.info(f'[{self._server.currentTerm}][{self._server.name}] starting an election.')
        lastLogIndex = self._server.log.last_log_index()

        election_message = PeerMessage.VoteMessage(self._server.rank, None, {'term': self._server.currentTerm, 
                                                                              'lastLogIndex' : lastLogIndex,
                                                                              'lastLogTerm' : self._server.log.last_log_term()})
        # Send message
        self._server.send_message(election_message)
    
    def on_append_entries_request(self, message, sender):
        ''' Leader with good term has already been elected has already '''
        if message.data['term'] < self._server.currentTerm:
            return
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] received RPC from leader, falling back to follower.')
        self._timer.cancel()
        self._server.change_state_to_follower()
        self._server.on_server(message, sender)
    
    def on_client_message(self, message, sender):
        ''' Telling client there is no leader '''
        logger.info(f'[{self._server.currentTerm}][{self._server.name}] request leader rank from {str(sender)} - answering {self._server.leader_rank}.')
        response = PeerMessage.RedirectionMessage(self._server.rank, message.sender, {'leader_rank':self._server.leader_rank})
        self._server.send_message(response, sender)

    def on_repl_recover(self, message):
        self._timer.cancel()
        self._server.is_running = True
        self._server.change_state_to_follower()

    def on_repl_crash(self, message):
        self._timer.cancel()
        self._server.is_running = False
