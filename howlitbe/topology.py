import dataclasses

import ipaddress
import math
import matplotlib
import matplotlib.pyplot
import networkx as nx
import os
import struct
import tired.logging

import howlitbe.topology


class _Enumeration:
    """
    Enables derived instances to be have a hashable unique identifier. Each hash
    is unique within a class, hashes may repeat between classes.
    """

    __bound = dict()
    """
    Class-specific id
    """

    __absolute_bound: int = 0
    """
    Unique global id
    """

    def __init__(self):
        """
        objtype - type of the object
        """
        # Assign class identifier
        if self.__class__.__name__ not in _Enumeration.__bound:
            _Enumeration.__bound[self.__class__.__name__] = 0
        self.__identifier = _Enumeration.__bound[self.__class__.__name__]
        _Enumeration.__bound[self.__class__.__name__] += 1

        # Assign absolute identifier
        self.__absolute_identifier = _Enumeration.__absolute_bound
        _Enumeration.__absolute_bound += 1

    def get_id(self):
        """ Returns unique id within this type """
        return self.__identifier

    def __hash__(self):
        return self.__absolute_identifier


class Node(_Enumeration):
    """
    Base class for network's node
    """
    pass
    def __init__(self, cpufrac: float = None):
        """
        cpufrac: fraction of overall CPU time for a particular host. [NOUNIT], fraction value.
        If None, no limit is used
        """
        _Enumeration.__init__(self)
        self.cpufrac = cpufrac  # Mininet (hence containernet too) allows setting CPU time fraction through utilizing linux CFS (https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html). See "mininet", CPULimitedHost, and "setCPUFrac()" (https://mininet.org/api/classmininet_1_1node_1_1CPULimitedHost.html)

    def get_ip4(self) -> int:
        """ Generate IP by the node's id """
        key = "HWL_IP_NETWORK"
        value = os.getenv(key, "10.0.0.0/24")
        tired.logging.info(f"Environment variable {key}=\"{value}\"")
        network = ipaddress.ip_network(value)
        address = network.network_address
        address = struct.unpack(">I", address.packed)[0]
        address = address | self.get_id()
        return address

    def get_ip4_string(self) -> str:
        return str(ipaddress.ip_address(self.get_ip4()))


class Switch(_Enumeration):
    """
    Representation of a network switch
    """
    def __init__(self, is_gate: bool):
        """
        - is_gate: whether the switch is a gate switch
        """
        _Enumeration.__init__(self)
        self.is_gate = is_gate


class PhysicalLink(_Enumeration):
    """ Physical connection between nodes """

    def __init__(self, node1: Node or Switch, node2: Node or Switch, bandwidth: int):
        """
        bandwidth: max network bandwidth, [b/s]. TODO: re-check units, how it is implemented in the containernet itself.
        """
        self.node1 = node1  # Endpoint 1
        self.node2 = node2  # Endpoint 2
        self.bps = bandwidth  # Mininet (hence containernet too) allows setting bandwidth for a link. See "--bw" option.
        _Enumeration.__init__(self)


class Container(_Enumeration):
    """
    A virtualized application. Container (or VM) is running on a physical node.
    """
    def __init__(self, node: Node, cpufrac: float, networkfrac: float, hddfrac: float, name: str):
        """
        - cpufrac: scaled max. allowed CPU value from 0 to 1. [NOUNIT], fraction
        - networkfrac: scaled max. allowed network bandwidth. [NOUNIT], fraction
        - hddfrac: scaled max. fraction of bandwidth when accessing storage devices. [NOUNIT], fraction
        - name: name of the container, or VM, that is getting deployed
        """
        self.node = node  # Node which the container is running on
        self.cpufrac = cpufrac  # Docker allows setting cpu limits. See --cpu-quota, --cpu-period, --cpu-shares. See https://docs.docker.com/engine/containers/resource_constraints/#configure-the-default-cfs-scheduler
        self.networkfrac = networkfrac  # Docker does not allow setting network bandwidth. However, it is possible through tc command, see `man tc (RATES)`, and https://stackoverflow.com/questions/25497523/how-can-i-rate-limit-network-traffic-on-a-docker-container
        self.hddfrac = hddfrac  # Docker allows limiting access for a particular piece of block device, virtualized, or otherwise. See --device-read-bps, https://stackoverflow.com/questions/36145817/how-to-limit-io-speed-in-docker-and-share-file-with-system-in-the-same-time
        self.name = name
        _Enumeration.__init__(self)


class OverlayContainer(Container):
    """
    Overlay container from the LB22 paper
    TODO: The assigned id will be within the type "OverlayContainer"
    """
    def __init__(self, node: Node, cpufrac: float, networkfrac: float, hddfrac: float, name: str, overlay_id: int):
        Container.__init__(self, node, cpufrac, networkfrac, hddfrac, name)
        self.overlay_id = overlay_id


def test_enumeration():
    import tired.logging
    tired.logging.info("Test whether the enumeration works for an instance that is derived from it")
    n1 = Node()
    n2 = Node()
    tired.logging.debug("Created nodes w/ global ids", str(hash(n1)), str(hash(n2)))
    pl = PhysicalLink(n1, n2, 0.5)
    tired.logging.debug("Global id for", pl.__class__.__name__, "is", str(hash(pl)))
    c1 = Container(node=n1, cpufrac=1.0, networkfrac=1.0, hddfrac=1.0, name="simpleserver")
    tired.logging.debug("Global id for", c1.__class__.__name__, "is", str(hash(c1)))
    assert(pl.get_id() == 0)
    assert(n1.get_id() == 0)
    assert(n2.get_id() == 1)
    assert(c1.get_id() == 0)
    id_list = list(map(lambda i: hash(i), [n1, n2, pl, c1]))
    tired.logging.debug("Ids", str(id_list))
    assert(len(id_list) == len(set(id_list)))


class Topology(nx.Graph):
    """
    - TODO: measure performance through creating artificial requests
    """

    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def as_nxgraph(self):
        return self.graph

    def render(self):
        """
        Render matplotlib plot w/ coloration:
        - orange - switches
        - green - gate switches
        - blue - nodes
        """
        def __node_color(node_data):
            if type(node_data) is Switch:
                color = "orange"
                if node_data.is_gate:
                    color = "green"
            else:
                color = "blue"

            return color
        nx_graph = self.as_nxgraph()
        colors = [__node_color(nx_graph.nodes[i]["data"]) for i in nx_graph.nodes()]
        nx.draw(nx_graph, with_labels=True, node_color=colors)
        matplotlib.pyplot.show()

    @staticmethod
    def new_topology_lb22_overlay(
            n_switches_total: int,
            n_gates: int,
            n_nodes: int,
            images_count: dict,
            n_overlays: int):
        """
        Generates a random virtualized network
        - n_switches_total - total number of switches (including externally-connected ones)
        - n_nodes - number of physical nodes
        - image_count - {image name: number of images}.

        - Containerized applications that will be running on the nodes.
        - Containers WILL BE randomly distributed among nodes.
        - Image names MAY repeat on a single node.
        - IF possible, each overlay WILL host at least 1 of each image type (just distribution)
        - Images will be RANDOMLY deployed on nodes.

        - n_overlays: number interconnected containers, or VMs that the system hosts.
        Within overlays, applications ONLY talk to each other. (i node, i
        overlay, image_name) together form a unique identifier of a container.
        This is required for the '22 paper aprobation.
        """
        tired.logging.info("Generating random topology with", str(n_switches_total), "switches (total),",
                str(n_gates), "gate switches,", str(n_nodes), "nodes,", "images:",
                str(images_count), str(n_overlays), "overlays")

        # Generate physical structure
        nodes = [Node(cpufrac=1.0) for _ in range(n_nodes)]
        switches = [Switch(is_gate=False) for _ in range(n_switches_total)]
        for i in range(n_gates):
            switches[i].is_gate = True
        # Generate containers
        n_containers = sum(images_count.values())
        containers = [OverlayContainer(node=None, cpufrac=1.0, networkfrac=1.0, hddfrac=1.0, name="", overlay_id=None) for _ in range(n_containers)]

        # Distribute containers among overlays (assign overlay types to containers)
        overlay_map = {o: list() for o in range(n_overlays)}  # {overlay id: list of containers}. Temporary index for fast access
        c = 0
        while c < n_containers:
            # Ensure image diversity (just distribution of image types across overlays)
            for i in images_count.keys():
                for o in range(n_overlays):
                    if images_count[i] > 0 and c < n_containers:
                        containers[c].overlay_id = o
                        containers[c].name = i  # Named after the image
                        images_count[i] -= 1
                        overlay_map[o].append(containers[c])
                        c+=1

        # Distribute containers among nodes. Ensure no more than 1 overlay type on each node
        c = 0
        while c < n_containers:
            for o in range(n_overlays):
                for n in range(n_nodes):
                    if c < n_containers and len(overlay_map[o]) > 0:
                        overlay_map[o][-1].node = nodes[n]
                        overlay_map[o] = overlay_map[o][:-1]  # Remove the last element
                        c += 1

        # Connect switches - create tree topology
        g = nx.Graph()
        # Create switch tree
        n_hops = 2
        n_switches_per_hop = int(math.ceil(n_switches_total ** (1 / n_hops)))
        if n_switches_per_hop < 1:
            n_switches_per_hop = 1
        # Initial conditions, counters
        s = 1
        switch_stack = [switches[0]]  # Stack containing the last switch for depth-first traverse
        switch_counter_stack = [n_switches_per_hop]  # Stack of hop counters for depth-first traverse
        hop = 0
        while s < n_switches_total:
            if hop >= n_hops:
                # Enforce hop ceiling, go one hop down
                hop-=1
                switch_counter_stack.pop()
                switch_stack.pop()
            else:
                if switch_counter_stack[-1] > 0:
                    # Hop is required
                    node1 = switch_stack[-1]
                    node2 = switches[s]
                    g.add_node(hash(node1), data=node1)
                    g.add_node(hash(node2), data=node2)
                    link = PhysicalLink(node1=switch_stack[-1], node2=switches[s], bandwidth=10)  # TODO: the bandwidth is wrong
                    tired.logging.debug(f"Adding link between switches {hash(node1)} and {hash(node2)}")
                    g.add_edge(hash(node1), hash(node2), relationship=link)
                    switch_counter_stack[-1] -= 1
                    switch_counter_stack.append(n_switches_per_hop)
                    switch_stack.append(switches[s])
                    s += 1
                    hop += 1
                elif hop > 0:
                    # Exhausted the number of hops, go one hop down
                    hop -= 1
                    switch_counter_stack.pop()
                    switch_stack.pop()
                else:
                    tired.logging.error("Unexpected premature stack exhaustion")
                    raise ValueError

        # Connect nodes to switches
        n_nodes_per_switch = int(math.ceil(n_nodes / n_switches_total))
        for n in range(n_nodes):
            node1 = nodes[n]
            g.add_node(hash(node1), data=node1)
            s = int(n / n_nodes_per_switch)
            switch = switches[s]
            link=PhysicalLink(node1=nodes[n], node2=switch, bandwidth=10)  # TODO: check the bw, it's wrong
            g.add_node(hash(switch), data=switch)
            g.add_edge(hash(node1), hash(switch), relationship=link)

        # Build the object
        ret = Topology(g)
        return ret


def test_lb22_topology_generation():
    should_run = os.getenv("HWL_TEST_LB22_TOPO", None)
    tired.logging.info(f"Environment variable HWL_TEST_LB22_TOPO={should_run} (Whether to run the test)")
    if not should_run:
        tired.logging.info("Skipping the test")
        return

    topology = Topology.new_topology_lb22_overlay(n_switches_total=5,
            n_gates=1,
            n_nodes=20,
            images_count={
                "image 1": 30,
                "image 2": 30,
            },
            n_overlays=5)
    topology.render()
