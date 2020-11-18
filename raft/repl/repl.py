import cmd

import logging

logger = logging.getLogger(__name__)

class RaftRepl(cmd.Cmd):
    intro = '=== pyraft repl in to interact with created cluster. Type help or ? to list commands. ===\n'
    prompt = '(pyraft) >>> '

    def __init__(self, cluster, transport, message_factory):
        super().__init__(self)
        self.cluster = cluster
        self.transport = transport
        self.message_factory = message_factory

    def do_SPEED(self, arg : str):
        parsed = arg.split()
        receiver = int(parsed[0])
        speed = parsed[1]
        
        msg = self.message_factory.SpeedMessage('repl', receiver, speed)
        self.transport.sendo(msg, receiver)

        logger.info(f'[REPL] sending SPEED("{speed}") message to {receiver}.')


    def do_CRASH(self, arg : str):
        parsed = arg.strip()
        receiver = int(parsed)

        msg = self.message_factory.CrashMessage('repl', receiver)
        self.transport.sendo(msg, receiver)

        logger.info(f'[REPL] sending CRASH message to {receiver}.')

    def do_START(self, arg : str):
        logger.info('[REPL] sending START message.')

        msg = self.message_factory.StartMessage('repl', None)
        for receiver in self.cluster:
            msg.receiver = receiver
            self.transport.sendto(msg, receiver)

    def do_RECOVERY(self, arg : str):
        print(arg)

    # ==========================

    def do_EXIT(self, arg : str):
        return True


    def precmd(self, line: str) -> str:
        if 'help' in line:
            return line

        return line.upper()
