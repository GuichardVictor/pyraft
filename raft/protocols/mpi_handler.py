# MPI import
import asyncio

from mpi4py import MPI

# Using OPEN MPI

class MPIProtocol:
    def __init__(self, node):
        self.node = node

    def data_received(self, msg):
        sender = msg.sender

        if sender == 0:
            self.node.on_client(msg)
        else:
            self.node.on_message(msg, sender)

class MPITransport:
    def __init__(self, protocol):
        self._protocol = protocol

    def sendto(self, message, receiver):
        comm = MPI.COMM_WORLD
        receiver = int(receiver)
        comm.send(message, dest=receiver)

    async def recv_handler(self):
        message = await MPITransport._waiting_for_message()
        self._protocol.data_received(message)
        asyncio.ensure_future(self.recv_handler())

    def start(self):
        asyncio.ensure_future(self.recv_handler())

    @staticmethod
    async def _waiting_for_message():
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        
        complete = False
        req = comm.irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
        
        while not complete:
            await asyncio.sleep(0.1)
            complete, message = req.test()
        
        return message

def create_mpi_server(server):
    protocol = MPIProtocol(server)
    transport = MPITransport(protocol)
    asyncio.ensure_future(transport.recv_handler())
    print(f'Serving on rank {MPI.COMM_WORLD.Get_rank()}')

    return transport