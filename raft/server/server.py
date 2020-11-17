from ..states.follower import Follower
from ..states.leader import Leader
from ..states.candidate import Candidate

import pickle

class ServerNode:
    def __init__(self, rank, state=None, cluster=[]):
        self.name = str(rank)
        self.rank = rank
        
        self.state = state if state is not None else Follower()
        self.state.set_server(self)
        self.transport = None

        self.cluster = cluster
        self.total_nodes = len(cluster)
        
        self.log_size = 5 #arbitrary and useless for now

        self.term = 0 # FIXME
    
    def on_message(self, message, sender):
        self.state.on_message(message, sender)

    def change_state(self, state):
        if isinstance(self.state, state.__class__):
            return

        self.state = state
        state.set_server(self)

        if isinstance(self.state, Leader):
            self.state.heartbeat()
        elif isinstance(self.state, Candidate):
            self.state.start_election()
        elif isinstance(self.state, Follower):
            return
        else:
            raise

    def on_client(self, message):
        pass

    def send_message(self, message, to=None):
        if to is None:
            self.broadcast_message(message)
        else:
            self.transport.sendto(message, to)

    def broadcast_message(self, message):
        for rank in self.cluster:
            if rank == self.rank:
                continue
            message.receiver = rank
            self.send_message(message, rank)