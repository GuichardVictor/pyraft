from raft.server.server import ServerNode
from raft.states.follower import Follower
from raft.states.candidate import Candidate

from raft.protocols.handler import ServerProtocol, ClientProtocol, create_server
from raft.protocols.mpi_handler import MPIProtocol, MPITransport, create_mpi_server
from mpi4py import MPI

import asyncio
import sys
import logging

logging.basicConfig(
    format='[%(asctime)s][%(levelname)4s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def main(argc, argv):
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size
    nb_client = 1

    cluster = list(range(nb_client, size))

    if rank == 0:
        return

    raft_node = ServerNode(rank, cluster=cluster)
    raft_node.transport = create_mpi_server(raft_node)
    # server = create_server(ip, port, raft_node)

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except:
        pass

    # clean async io server
    loop.close()


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)