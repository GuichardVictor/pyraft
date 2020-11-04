class Message:
    VoteMessageType = 0
    VoteResponseType = 1
    HeartBeatType = 2
    HeartBeatResponseType = 3
    
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