import dataclasses
import howlitbe.topology

@dataclasses.dataclass
class VirtualizedNetworkTechnology:
    """
    Scheduled amount of data to transfer, process, or store, on each node
    """

    topology: howlitbe.topology.Topology
    """ Network topology """

    traffic: dict
    """
    Map of format: {((howlitbe.topology.Node howlitbe.topology.Node): N}, where
    N - bytes.

    Planned (calculated optimal) traffic between nodes.
    """


@dataclasses.dataclass
class Scenario:
    nodes: list
    """ An array of nodes in the network"""

network_technology =
