"""
2024 paper. Abrobation of the ideas formulated in 2022's paper on network
balancing.

Paper citation:
Мурашов, Д.А. and Ушаков, В.А., 2022. Постановка и анализ путей решения задачи
синтеза программ управления и параметров информационно-вычислительной сети на
основе полимодельного описания. Авиакосмическое приборостроение, (8), pp.23-32.

TL; DR
The model describes a set of virtualized overlay networks hosted on a real
physical network, a set of docker containers communicating w/ e/o within one
overlay. Objectives: how to route the traffic b/w nodes, and how to distribute
physical resources b/w docker containers, so the amount of information we
process is maximized.
"""

import dataclasses
import howlitbe.topology
import networkx as nx
import twoopt.linsmat
import twoopt.data_processing.vector_index


@dataclasses.dataclass
class VirtualizedNetworkTechnology:
    """
    Scheduled amount of data to transfer, process, or store, on each node.
    Reflects the model from '23 paper exactly, but during deployment, the result
    of its interpretation may differ.

    The technology MUST be designed in the model's terms w.r.t. to the following
    subject area specificities:
    - type of node (switch, processor, controller?)

    In some sense, it can be considered a scenario

    - TODO: add failure scenario
    """

    topology: nx.Graph
    """ Network topology """

    # The following parameters are calculated by the linear programming model

    traffic: map
    """{(l, j, i, rho): N}, where l - structural stability span index, N bytes, j - node id (from), i - node it (to), rho - container net"""

    processing: map
    """{(l, j, rho): N}, l - structural stability span index, N bytes, j - node id, rho - container overlay network"""

    storage: map
    """{(l, j, rho): N}, l - structural stability span index, N bytes, j - node i, rho - container overlay network"""

    drop: map
    """{(l, j, rho): N}, l - structural stability span index, N bytes, j - node i, rho - container overlay network"""

    # The following parameters are calculated by the GA-based model

    network_bandwidth_limit: map
    """{(l, j, rho): F}, l - structural stability span index j - node, rho - container overlay network, F - fraction"""

    memory_bandwidth_limit: map
    """{(l, j, rho): F}, l - structural stability span index j - node, rho - container overlay network, F - fraction"""

    cpu_limit: map
    """{(l, j, rho): F}, l - structural stability span index, j - node, rho - container overlay network, F - fraction"""

    @staticmethod
    def new_replication_scenario(j_max: int,
                        rho_max: int,
                        n_databases: int,
                        n_switches_total: int,
                        n_gates: int,
                        inbound_traffic_bytes: int,
                        outbound_traffic_bytes: int) -> object:
        """
        "Replication" scenario, 3 structural stability intervals:
        1. A networks operates normally;
        2. Replication starts, 2 database nodes detach from the network;
        3. A network continues operating normally;

        j_max - number of nodes, total (including databases and switches)
        rho_max - number of overlays
        n_databases - number of nodes whose primary responsibility is to store, and produce (respond to queries) data
        n_switches - total number of switches (including externally-connected ones)
        n_ingress - number of externally-connected switches
        inbound_traffic_bytes - number of bytes that enter the network
        outbound_traffic_bytes - number of bytes that exit the network

        From a set of parameters, generates network topology, structural
        stability intervals, constraints, runs linear solver, and initializes
        the object with calculated planned values.
        """

        # Describes used variables, variable indices, and bounds thereof. Used for linear equation matrix building
        schema = twoopt.data_processing.Schema(data={
            "indexbound": {
                "j": 5, # TODO
            },
            "variableindices": {
                "alpha_0": [],  # Relative importance of maximizing the amount of processed data
                "alpha_1": [],  # Relative importance of minimizing the amount of dropped data
                "x": ["j", "i", "rho", "l"],  # Amount of transferred data
                "y": ["j", "rho", "l"],  # Amount of stored data
                "g": ["j", "rho", "l"],  # Amount of processed data
                "z": ["j", "rho", "l"],  # Amount of dropped data
                "x_eq": ["j", "rho", "l"],  # Balance offset, positive for ingress nodes, negative for outgress
            }
        })
