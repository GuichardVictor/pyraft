import time
import random
from ..messages.message import Message

class State:
    def set_server(self, server):
        self._server = server

    def on_message(self, message, sender):
        if message.type == Message.VoteMessageType:
            self.on_vote_request(message, sender)
        
        if message.type == Message.VoteResponseType:
            self.on_vote_received(message, sender)

        if message.type == Message.HeartBeatType:
            self.on_heartbeat(message, sender)
        
        if message.type == Message.HeartBeatResponseType:
            self.on_heartbeat_response(message, sender)

        elif message.type == Message.UndefinedType:
            raise

    def on_vote_request(self, message, sender):
        pass

    def on_vote_received(self, message, sender):
        pass

    def on_heartbeat(self, message, sender):
        pass

    def on_heartbeat_response(self, message, sender):
        pass

    def _get_next_timeout(self):
        # randomized election timeouts
        return random.randrange(self.timeout, 2 * self.timeout)