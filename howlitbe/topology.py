import dataclasses


@dataclasses.dataclass
class Node:
    """
    Base class for network's node
    """
    pass


@dataclasses.dataclass
class PhysicalLink:
    """ Physical connection between nodes """
    node1: Node
    node2: NOde


@dataclasses.dataclass
class Topology:
    """
    Describes network topology, and configuration: nodes, containers, links,
    properties thereof
    """
    pass


@dataclasses.dataclass
class Container:
    node: Node
    """ A node on which the container is running """
