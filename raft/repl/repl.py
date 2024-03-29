import cmd
import sys

import logging

from ..messages.message import ReplMessage

logger = logging.getLogger(__name__)

class RaftRepl(cmd.Cmd):
    intro = '=== pyraft repl in to interact with created cluster. Type help or ? to list commands. ===\n'
    prompt = '(pyraft) >>> '

    def __init__(self, cluster, transport):
        super().__init__()
        self.cluster = cluster
        self.transport = transport

    def _check_receiver(self, receiver):
        return receiver in self.cluster
    
    def _check_speed(self, speed):
        return speed in ['SLOW', 'MEDIUM', 'FAST']

    def do_SPEED(self, arg : str):
        ''' Set Process Speed.
        
        Usage: SPEED rank [SLOW:MEDIUM:FAST]
        '''
        parsed = arg.split()
        receiver = int(parsed[0])
        speed = parsed[1]

        if self._check_receiver(receiver) is False or self._check_speed(speed) is False:
            raise ValueError

        data = {'speed' : speed}
        msg = ReplMessage.SpeedMessage('repl', receiver, data)
        self.transport.sendto(msg, receiver)

        logger.info(f'[REPL] sending SPEED("{speed}") message to {receiver}.')

    def do_CRASH(self, arg : str):
        ''' Block Process Communication.
        
        Usage: CRASH rank
        '''
        parsed = arg.strip()

        receiver = int(parsed)

        if self._check_receiver(receiver) is False:
            raise ValueError

        msg = ReplMessage.CrashMessage('repl', receiver)
        self.transport.sendto(msg, receiver)

        logger.info(f'[REPL] sending CRASH message to {receiver}.')

    def do_START(self, arg : str):
        ''' Start the program
        
        Usage: START
        '''
        logger.info('[REPL] sending START message.')

        msg = ReplMessage.StartMessage('repl', None)
        for receiver in self.cluster:
            msg.receiver = receiver
            self.transport.sendto(msg, receiver)
    
    def do_STOP(self, arg : str):
        ''' Stop all servers and clients
        
        Usage: STOP
        '''
        logger.info('[REPL] sending STOP message.')

        msg = ReplMessage.StopMessage('repl', None)
        for receiver in self.cluster:
            msg.receiver = receiver
            self.transport.sendto(msg, receiver)

    def do_RECOVERY(self, arg : str):
        ''' Recover a process and reset its state
        
        Usage: RECOVERY rank
        '''
        parsed = arg.strip()

        receiver = int(parsed)
        if self._check_receiver(receiver) is False:
            raise ValueError

        msg = ReplMessage.RecoverMessage('repl', receiver)
        self.transport.sendto(msg, receiver)

        logger.info('[REPL] sending RECOVER message to {receiver}.')


    # ==========================

    def onecmd(self, line: str) -> bool:
        try:
            return super().onecmd(line)
        except Exception as e:
            logger.error(f"[REPL] Failed line: {line}")
        return False

    def do_EXIT(self, arg : str):
        ''' exit the repl (if STOP was not called CTRL+C will need to be used)'''
        return True

    def do_EOF(self, arg):
        ''' Made to handle ctrl+c SIGINT'''
        return True

    def precmd(self, line: str) -> str:
        if 'help' in line:
            return line

        return line.upper()
