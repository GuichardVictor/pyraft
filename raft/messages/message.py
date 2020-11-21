class Message:
    PeerMessageType = 0
    VoteMessageType = 1
    VoteResponseType = 2
    AppendEntryMessageType = 3
    AppendEntryResponseType = 4
    RedirectionMessageType = 5
    ServerEntryResponseType = 6
    ServerHeartbeatMessageType = 7


    ClientMessageType = 10
    ClientEntryMessageType = 11

    ReplMessageType = 20
    ReplCrashMessageType = 21
    ReplStartMessageType = 22
    ReplSpeedMessageType = 23


    UndefinedType = -1

    def __init__(self, sender, receiver, data):
        self.sender = sender
        self.receiver = receiver
        self.data = data

        self.global_type = None
        self.message_type = None

    @property
    def source_type(self):
        return self.global_type

    @property
    def type(self):
        return self.message_type

class PeerMessage(Message):
    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, data)
        self.global_type = Message.PeerMessageType

    @staticmethod
    def VoteMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.VoteMessageType
        return msg

    @staticmethod
    def VoteResponse(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.VoteResponseType
        return msg

    @staticmethod
    def AppendEntryMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.AppendEntryMessageType
        return msg

    @staticmethod
    def AppendEntryResponse(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.AppendEntryResponseType
        return msg

    @staticmethod
    def RedirectionMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.RedirectionMessageType
        return msg

    @staticmethod
    def ServerEntryResponse(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.ServerEntryResponseType
        return msg

    @staticmethod
    def ServerHeartbeatMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.ServerHeartbeatMessageType
        return msg

class ClientMessage(Message):
    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, data)

        self.global_type = Message.ClientMessageType

    
    @staticmethod
    def ClientEntryMessage(sender, receiver, data):
        msg = ClientMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.ClientEntryMessageType
        return msg

class ReplMessage(Message):

    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, data)

        self.global_type = Message.ReplMessageType

    @staticmethod
    def ClientEntry(sender, receiver, speed):
        data = speed
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.ReplSpeedMessageType

        return msg

    @staticmethod
    def StartMessage(sender, receiver):
        data = None
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.ReplStartMessageType

        return msg

    @staticmethod
    def CrashMessage(sender, receiver):
        data = None
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = Message.ReplCrashMessageType

        return msg