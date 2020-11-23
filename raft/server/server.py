from ..states.follower import Follower
from ..states.leader import Leader
from ..states.candidate import Candidate
from ..log.log import LogManager
import pickle

import time
import logging

logger = logging.getLogger(__name__)


class ServerNode:
    def __init__(self, rank, cluster, timeout_list):
        self.name = str(rank)
        self.rank = rank

        self.state = Follower(timeout_list[0])
        self.state.set_server(self)
        self.transport = None
        self.sleep_time = 0

        self.cluster = cluster
        self.total_nodes = len(cluster)
        self.is_running = False
        self.log_size = 0 #arbitrary and useless for now
        self.log = LogManager(rank)

        self.leader_rank = None
        self.currentTerm = 0 
        self.timeout_list = timeout_list

        self.commitIndex = 0
        self.lastApplied = 0

    def on_server(self, message, sender):
        if not self.is_running:
            return
        time.sleep(self.sleep_time/2)
        sender_term = message.data['term']
        if sender_term > self.currentTerm:
            self.state._timer.cancel()
            self.currentTerm = sender_term
            if not isinstance(self.state, Follower):
                logger.info(f'[{self.currentTerm}][{self.name}] had term outdated, falling back to follower.')
                self.change_state_to_follower()
        self.state.on_peer_message(message, sender)

    def on_client(self, message, sender):
        if not self.is_running:
            return
        time.sleep(self.sleep_time/2)
        self.state.on_client_message(message, sender)

    def on_repl(self, message):
        self.state.on_repl_message(message)

    def change_state_to_follower(self):
        self.change_state(Follower(self.timeout_list[0]))

    def change_state_to_candidate(self):
        self.change_state(Candidate(self.timeout_list[1]))

    def change_state_to_leader(self):
        self.change_state(Leader(self.timeout_list[2]))

    def change_state(self, state):
        if isinstance(self.state, state.__class__):
            return

        self.state = state
        state.set_server(self)

        if isinstance(self.state, Leader):
            self.state.setup()
            self.state.send_append_entries()
        elif isinstance(self.state, Candidate):
            self.state.start_election()
        elif isinstance(self.state, Follower):
            return
        else:
            raise NotImplementedError

    def send_message(self, message, to=None, speed=True):
        if speed:
            time.sleep(self.sleep_time/2)
        if to is None:
            self.broadcast_message(message)
        else:
            self.transport.sendto(message, to)

    def broadcast_message(self, message):
        for rank in self.cluster:
            if rank == self.rank:
                continue
            message.receiver = rank
            self.send_message(message, rank, False)