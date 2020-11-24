import asyncio
import sys
import logging

from mpi4py import MPI
from raft.protocols.mpi_handler import MPITransport, create_mpi_server

from raft.server.server import ServerNode
from raft.client.client import ClientNode
from raft.repl import RaftRepl

logging.basicConfig(
    format='[%(asctime)s][%(levelname)4s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def init_client_node(rank, cluster, timeout_client):
    raft_client = ClientNode(rank, cluster, timeout_client)
    raft_client.transport = create_mpi_server(raft_client)

def init_server_node(rank, cluster, timeout_list):
    raft_node = ServerNode(rank, cluster, timeout_list)
    raft_node.transport = create_mpi_server(raft_node)

def init_repl(nb_node):
        # REPL
    transport = MPITransport(None)
    cluster = list(range(1, nb_node))

    RaftRepl(cluster, transport).cmdloop()
    
    MPI.Finalize()

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

    coef = 20 # for debug
    timeout_list = list(map(lambda elt: elt * coef, timeout_list))
    timeout_client *= coef

    if rank == 0:
        init_repl(size)
        return

    elif rank > 0 and rank <= nb_client:
        init_client_node(rank, cluster, timeout_client)

    else:
        init_server_node(rank, cluster, timeout_list)

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