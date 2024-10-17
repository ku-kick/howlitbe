"""
2024 paper. Abrobation of the ideas formulated in 2022's paper on network
balancing.

Paper citation:
Мурашов, Д.А. and Ушаков, В.А., 2022. Постановка и анализ путей решения задачи
синтеза программ управления и параметров информационно-вычислительной сети на
основе полимодельного описания. Авиакосмическое приборостроение, (8), pp.23-32.
"""

import dataclasses
import howlitbe.topology
import networkx as nx


@dataclasses.dataclass
class VirtualizedNetworkTechnology:
    """
    Scheduled amount of data to transfer, process, or store, on each node.
    Reflects the model from '23 paper exactly, but during deployment, the result
    of its interpretation may differ.

    The technology MUST take the following specifics into consideration:
    - type of node (switch, processor, controller?)
    """

    topology: nx.Graph
    """ Network topology """

    traffic: map
    """ {(j, i, rho): N}, where N - bytes, j - node id (from), i - node it (to), rho - container net """

    processing: map
    """ {(j, rho): N}, N - bytes, j - node id, rho - container overlay network"""

    storage: map
    """ {(j, rho): N}, N - bytes, j - node i, rho - container overlay network """

    drop: map
    """ {(j, rho): N}, N - bytes, j - node i, rho - container overlay network """

    network_bandwidth_limit: map
    """{(j, rho): F}, j - node, rho - container overlay network, F - fraction"""

    memory_bandwidth_limit: map
    """{(j, rho): F}, j - node, rho - container overlay network, F - fraction"""

    cpu_limit: map
    """{(j, rho): F}, j - node, rho - container overlay network, F - fraction"""


@dataclasses.dataclass
class Scenario:
    pass
