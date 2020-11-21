class Message:
    VoteMessageType = 0
    VoteResponseType = 1
    HeartBeatType = 2
    HeartBeatResponseType = 3
    
    ClientMessageType = 10
    ReplMessageType = 20

    UndefinedType = -1

    def __init__(self, sender, receiver, term, data):
        self.sender = sender
        self.receiver = receiver
        self.term = term
        self.data = data

        self.message_type = None

    @property
    def type(self):
        return self.message_type

class VoteMessage(Message):
    def __init__(self, sender, receiver, term, data):
        super().__init__(sender, receiver, term, data)
        self.message_type = Message.VoteMessageType

class VoteResponse(Message):
    def __init__(self, sender, receiver, term, data):
        super().__init__(sender, receiver, term, data)
        self.message_type = Message.VoteResponseType


class HeartBeatMessage(Message):
    def __init__(self, sender, receiver, term, data):
        super().__init__(sender, receiver, term, data)
        self.message_type = Message.HeartBeatType

class HeartBeatResponse(Message):
    def __init__(self, sender, receiver, term, data):
        super().__init__(sender, receiver, term, data)
        self.message_type = Message.HeartBeatResponseType

class ClientMessage(Message):
    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, 0, data)

        self.message_type = Message.ClientMessageType

class ReplMessage(Message):

    ReplSpeedType = 0
    ReplStartType = 1
    ReplCrashType = 2
    ReplRecoverType = 3

    UndefinedType = -1

    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, 0, data)

        self.message_type = Message.ReplMessageType
        self.repl_type = None

    @staticmethod
    def SpeedMessage(sender, receiver, speed):
        data = speed
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.repl_type = ReplMessage.ReplSpeedType

        return msg

    @staticmethod
    def StartMessage(sender, receiver):
        data = None
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.repl_type = ReplMessage.ReplStartType

        return msg

    @staticmethod
    def CrashMessage(sender, receiver):
        data = None
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.repl_type = ReplMessage.ReplCrashType

        return msg

    @staticmethod
    def RecoverMessage(sender, receiver):
        data = None
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.repl_type = ReplMessage.ReplRecoverType

        return msg