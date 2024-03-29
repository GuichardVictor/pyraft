# MPI import
import asyncio
from ..messages.message import Message

from mpi4py import MPI

# Using OPEN MPI

class MPIProtocol:
    ''' Dispatch messages when received from the transport '''
    def __init__(self, node):
        self.node = node

    def data_received(self, msg):
        message_type = msg.global_type

        if message_type == Message.ClientMessageType:
            self.node.on_client(msg, msg.sender)
        elif message_type == Message.ReplMessageType:
            self.node.on_repl(msg)
        else:
            self.node.on_server(msg, msg.sender)

class MPITransport:
    ''' Can be seen as a socket '''

    def __init__(self, protocol):
        self._protocol = protocol

    def sendto(self, message, receiver):
        comm = MPI.COMM_WORLD
        receiver = int(receiver)
        comm.send(message, dest=receiver)

    async def recv_handler(self):
        ''' Register in asyncio event loop to handle recv from MPI '''
        try:
            message = await MPITransport._waiting_for_message()
            self._protocol.data_received(message)

            asyncio.ensure_future(self.recv_handler())
        except asyncio.CancelledError:
            raise asyncio.CancelledError()

    def start(self):
        asyncio.ensure_future(self.recv_handler())

    @staticmethod
    async def _waiting_for_message():
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        
        complete = False
        req = comm.irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
        
        while not complete:
            await asyncio.sleep(0.01) # python await doesn't work with mpi
            complete, message = req.test()
        
        return message


def create_mpi_server(server):
    protocol = MPIProtocol(server)
    transport = MPITransport(protocol)
    asyncio.ensure_future(transport.recv_handler())
    print(f'Serving on rank {MPI.COMM_WORLD.Get_rank()}')

    return transport