class Message:
    ''' Base message class

    Message is defined by its global
    type and message type

    Args:
        sender: sender id
        receiver: receiver id
        data: python dict containing all required information
    '''
    PeerMessageType = 0
    ClientMessageType = 10
    ReplMessageType = 20
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
    ''' Server message class

    All message sent by a server ex 
    VoteMessageType: request a vote

    Args:
        sender: sender id
        receiver: receiver id
        data: python dict containing all required information
    '''
    VoteMessageType = 1
    VoteResponseType = 2
    AppendEntryMessageType = 3
    AppendEntryResponseType = 4
    RedirectionMessageType = 5
    ServerEntryResponseType = 6
    ServerHeartbeatMessageType = 7

    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, data)
        self.global_type = Message.PeerMessageType

    @staticmethod
    def VoteMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.VoteMessageType
        return msg

    @staticmethod
    def VoteResponse(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.VoteResponseType
        return msg

    @staticmethod
    def AppendEntryMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.AppendEntryMessageType
        return msg

    @staticmethod
    def AppendEntryResponse(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.AppendEntryResponseType
        return msg

    @staticmethod
    def RedirectionMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.RedirectionMessageType
        return msg

    @staticmethod
    def ServerEntryResponse(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.ServerEntryResponseType
        return msg

    @staticmethod
    def ServerHeartbeatMessage(sender, receiver, data):
        msg = PeerMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = PeerMessage.ServerHeartbeatMessageType
        return msg

class ClientMessage(Message):
    ''' Client message class

    Message sent by a client

    Args:
        sender: sender id
        receiver: receiver id
        data: python dict containing all required information
    '''
    ClientEntryMessageType = 11

    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, data)

        self.global_type = Message.ClientMessageType

    @staticmethod
    def ClientEntryMessage(sender, receiver, data):
        msg = ClientMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = ClientMessage.ClientEntryMessageType
        return msg

class ReplMessage(Message):
    ''' REPL message class

    All message sent by the REPL ex 
    ReplStartMessageType: start servers and clients

    Args:
        sender: sender id
        receiver: receiver id
        data: python dict containing all required information
    '''
    ReplCrashMessageType = 21
    ReplStartMessageType = 22
    ReplSpeedMessageType = 23
    ReplRecoverMessageType = 24
    ReplStopMessageType = 25

    def __init__(self, sender, receiver, data):
        super().__init__(sender, receiver, data)
        self.global_type = Message.ReplMessageType

    @staticmethod
    def SpeedMessage(sender, receiver, data):
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = ReplMessage.ReplSpeedMessageType
        return msg

    @staticmethod
    def StartMessage(sender, receiver, data=None):
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = ReplMessage.ReplStartMessageType
        return msg

    @staticmethod
    def CrashMessage(sender, receiver, data=None):
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = ReplMessage.ReplCrashMessageType
        return msg

    @staticmethod
    def RecoverMessage(sender, receiver, data=None):
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = ReplMessage.ReplRecoverMessageType
        return msg

    @staticmethod
    def StopMessage(sender, receiver, data=None):
        msg = ReplMessage(sender=sender, receiver=receiver, data=data)
        msg.message_type = ReplMessage.ReplStopMessageType
        return msg