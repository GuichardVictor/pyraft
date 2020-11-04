import asyncio
import pickle

import logging


logger = logging.getLogger(__name__)


# Only Using Asyncio: define serverprotocol using UDP, and a client Protocol in TCP
class ServerProtocol(asyncio.Protocol):
    """ Communicate with servers """
    def __init__(self, node):
        self.node = node

    def connection_made(self, transport):
        logger.info(f'Server connection made with {transport}')
        self.transport = transport

    def datagram_received(self, data, sender):
        message = pickle.loads(data)
        self.node.on_message(message, sender)

    def error_received(self, ex):
        print('Error:', ex)

class ClientProtocol(asyncio.Protocol):
    """ Communicate with clients """
    
    def __init__(self, node):
        self.node = node

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = pickle.loads(data)
        self.node.on_client(data)

    def connection_lost(self, exc):
        logger.debug(f'Client connection lost with {self.transport.get_extra_info("peername")}')
    
    def send(self, data):
        self.transport.write(pickle.dumps(data))
        self.transport.close()


def create_server(ip, port, raft_node):
    loop = asyncio.get_event_loop()
    
    coroutine = loop.create_datagram_endpoint(lambda: ServerProtocol(raft_node), local_addr=(ip, port))

    transport, _ = loop.run_until_complete(coroutine)
    raft_node.transport = transport
    
    coroutine = loop.create_server(lambda: ClientProtocol(raft_node), ip, port)

    server = loop.run_until_complete(coroutine)

    print(f'Serving on {ip}:{port}.')
    return server