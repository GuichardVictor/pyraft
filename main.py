from raft.server.server import ServerNode
from raft.states.follower import Follower
from raft.states.candidate import Candidate

from raft.protocols.handler import ServerProtocol, ClientProtocol, create_server
#from raft.protocols.mpi_handler import MPIProtocol, MPITransport, create_mpi_server

import asyncio
import sys
import logging

logging.basicConfig(
    format='[%(asctime)s][%(levelname)4s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def main(argc, argv):
    ip, port = '127.0.0.1', 8000
    cluster = [(ip, port), (ip, port+1), (ip, port+2)]

    if argc > 1:
        ip, port = str(argv[1]), int(argv[2])
    
    raft_node = ServerNode(ip, port, cluster=cluster)
    server = create_server(ip, port, raft_node)

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except:
        pass

    # clean async io server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)