import cmd

class RaftRepl(cmd.Cmd):
    intro = '=== pyraft repl in to interact with created cluster. Type help or ? to list commands. ===\n'
    prompt = '(pyraft) >>> '

    def __init__(self, cluster):
        super().__init__(self)
        self.cluster = cluster

    def do_SPEED(self, arg : str):
        print(arg)

    def do_CRASH(self, arg : str):
        print(arg)

    def do_START(self, arg : str):
        print(arg)

    def do_RECOVERY(self, arg : str):
        print(arg)

    # ==========================

    def do_EXIT(self, arg : str):
        return True


    def precmd(self, line: str) -> str:
        if 'help' in line:
            return line
        return line.upper()

if __name__ == '__main__':
    # Testing the REPL
    cluster = [1, 2, 3, 4]
    RaftRepl(cluster).cmdloop()