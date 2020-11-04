from ..states.follower import Follower
from ..states.leader import Leader
from ..states.candidate import Candidate

import pickle

class ServerNode:
    def __init__(self, ip, port, state=None, cluster=[]):
        self.name = ip + ':' + str(port)
        self.ip = ip
        self.port = port
        
        self.state = state if state is not None else Follower()
        self.state.set_server(self)
        self.transport = None

        self.cluster = cluster
        self.total_nodes = len(cluster)

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
            self.transport.sendto(pickle.dumps(message), to)

    def broadcast_message(self, message):
        for receiver in self.cluster:
            if receiver[0] == self.ip and receiver[1] == self.port:
                continue
            message.receiver = receiver
            self.send_message(message, receiver)