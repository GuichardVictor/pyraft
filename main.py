from raft.server.server import ServerNode
from raft.states.follower import Follower
from raft.states.candidate import Candidate
from raft.client.client import ClientNode

from raft.repl import RaftRepl
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
    if argc < 2:
        exit(1)
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size
    nb_client = int(argv[1])
    cluster = list(range(nb_client + 1, size))

    # order : timeout follower, timeout candidate, timeout leader
    timeout_list = [200, 200, 50]
    timeout_client = 500
    coef = 20#for debug
    timeout_list = list(map(lambda elt: elt * coef, timeout_list))
    timeout_client *= coef
    if rank == 0:
        # REPL
        transport = MPITransport(None)
        cluster = list(range(1, size))

        RaftRepl(cluster, transport).cmdloop()
        
        MPI.Finalize()
        return

    elif rank > 0 and rank <= nb_client:
        raft_client = ClientNode(rank, cluster, timeout_client)
        raft_client.transport = create_mpi_server(raft_client)

    else:
        raft_node = ServerNode(rank, cluster, timeout_list)
        raft_node.transport = create_mpi_server(raft_node)

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
        # Loop as stopped, let's ensure that everything is stopping properly
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        # Closing the loop
        loop.close()

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)