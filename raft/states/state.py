import time
import random
from ..messages.message import PeerMessage, ClientMessage, ReplMessage

import logging

logger = logging.getLogger(__name__)

class State:
    def set_server(self, server):
        self._server = server


    def on_repl_message(self, message):
        if message.type == ReplMessage.ReplStartMessageType:
            self.on_repl_start(message)

        if message.type == ReplMessage.ReplCrashMessageType:
            self.on_repl_crash(message)

        if message.type == ReplMessage.ReplSpeedMessageType:
            self.on_repl_speed(message)


    def on_client_message(self, message, sender):
        if message.type == ClientMessage.ClientEntryMessageType:
            self.on_client(message, sender)

    def on_peer_message(self, message, sender):

        if message.type == PeerMessage.VoteMessageType:
            self.on_vote_request(message, sender)
        
        if message.type == PeerMessage.VoteResponseType:
            self.on_vote_received(message, sender)

        if message.type == PeerMessage.AppendEntryMessageType:
            self.on_append_entries_request(message, sender)
        
        if message.type == PeerMessage.AppendEntryResponseType:
            self.on_append_entries_response(message, sender)


    def on_vote_request(self, message, sender):
        pass

    def on_vote_received(self, message, sender):
        pass

    def on_append_entries_request(self, message, sender):
        pass

    def on_append_entries_response(self, message, sender):
        pass

    def on_client(self, message, sender):
        pass



    def _get_next_timeout(self):
        # randomized election timeouts
        return random.randrange(self.timeout, 2 * self.timeout)