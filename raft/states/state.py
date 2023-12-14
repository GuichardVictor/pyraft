import time
import random
from ..messages.message import PeerMessage, ClientMessage, ReplMessage

import logging
import asyncio

logger = logging.getLogger(__name__)

class State:
    ''' Base class for state
    The class also handles the message dispatching according to types
    '''
    def set_server(self, server):
        self._server = server

    def on_repl_message(self, message):
        ''' Dispatches repl message'''
        if message.type == ReplMessage.ReplStartMessageType:
            self.on_repl_start(message)

        if message.type == ReplMessage.ReplCrashMessageType:
            self.on_repl_crash(message)

        if message.type == ReplMessage.ReplSpeedMessageType:
            self.on_repl_speed(message)

        if message.type == ReplMessage.ReplRecoverMessageType:
            self.on_repl_recover(message)

        if message.type == ReplMessage.ReplStopMessageType:
            self.on_repl_stop(message)
        

    def on_client_message(self, message, sender):
        ''' Dispatches client message'''
        if message.type == ClientMessage.ClientEntryMessageType:
            self.on_client(message, sender)

    def on_peer_message(self, message, sender):
        ''' Dispatches server message'''
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

    def on_repl_speed(self, message):
        ''' Compute time to sleep at recv and send '''
        percentage = 0
        if message.data['speed'] == 'MEDIUM':
            percentage = 25
        if message.data["speed"] == "SLOW":
            percentage = 50
        self.sleep_time = self.next_timeout * (percentage / 100.0)

    def on_repl_stop(self, message):
        ''' Cancel all asyncio tasks and stop loop '''
        loop = asyncio.get_event_loop()

        for task in asyncio.all_tasks():
            task.cancel()

        loop.stop()

        raise asyncio.CancelledError()

    def on_repl_start(self, message):
        pass

    def on_repl_crash(self, message):
        pass

    def on_repl_recover(self, message):
        pass

    def _get_next_timeout(self):
        # randomized timeouts
        value = random.randrange(self.timeout, 2 * self.timeout)
        return value / 1000