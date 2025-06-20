"""
Wrapper over mininet extending it w/ required functionality (primarily --
deployment of docker containers).

Using this wrapper requires extended version of Mininet environment (VM), the
one w/ docker. Please refer to 'tools/mininet-postinstall.sh'
"""


import howlitbe.mininet
import howlitbe.topology
import os
import tired.logging
import networkx as nx

# If containernet is not installed (development environment), dry run

def make_dry_run(classname: str):
    def mock_function(self, *args, **kwargs):
        return self

    class _DryRun:
        def __init__(self, *args, **kwargs):
            pass

        addDocker = mock_function
        addHost = mock_function
        addSwitch = mock_function
        addController = mock_function
        start = mock_function
        addLink = mock_function

    ret = _DryRun
    ret.__name__ = classname
    return ret


try:
    from mininet.net import Mininet
    from mininet.node import Controller
    from mininet.cli import CLI
    from mininet.link import TCLink
    from mininet.log import info, setLogLevel
    from mininet.link import Link
    from mininet.node import Node
    HWL_DRY_RUN = False
except ModuleNotFoundError as e:
    tired.logging.warning("Mocking containernet, because containernet is not installed")
    # The testbed environment is a non-virtualized machine without Containernet installed, keep to dry running
    Mininet = make_dry_run("Mininet")
    Containernet = make_dry_run("Mininet")
    Controller = make_dry_run("Controller")
    CLI = make_dry_run("CLI")
    TCLink = make_dry_run("TCLink")
    info = tired.logging.info
    HWL_DRY_RUN = True


class DeploymentBuilder:
    """ Builds Containernet object from a given topology """

    def build_from_topology(self, topology: howlitbe.topology.Topology):
        # Initialize the network
        net = Mininet(controller=Controller)
        # Create one default controller w/ a predefined name
        net.addController('c0')
        nodemap = dict()  # A temporary index for addressing the created mininet/containernet entities later
        # Spawn nodes and switches
        nx_graph = topology.as_nxgraph()
        for i in nx_graph.nodes():
            node = nx_graph.nodes[i]["data"]
            if isinstance(node, howlitbe.topology.Switch):
                switch_name = "s" + str(node.get_id())
                # TODO: Limits
                s = net.addSwitch(switch_name)
                tired.logging.debug(f"Built switch {switch_name}")
                nodemap[hash(node)] = s
            elif isinstance(node, howlitbe.topology.Node):
                # TODO: do we really need nodes for that? It might be so docker automatically create a host
                host_name = "h" + str(node.get_id())
                # TODO: Limits
                tired.logging.debug("Adding host", host_name, node.get_ip4_string())
                n = net.addHost(host_name,
                        ip=node.get_ip4_string(),
                        prefixLen=node.get_ip4_prefixlen())
                nodemap[hash(node)] = n
            elif isinstance(node, howlitbe.topology.Container):
                container_name = "d" + str(node.get_id())
                # TODO: Limits
                tired.logging.debug("Adding docker", container_name, "on node",
                        str(node.node.get_id()), "ip", node.node.get_ip4_string(),
                        "application", node.name)
                n = net.addDocker(node.get_string_id(),
                        ip=node.node.get_ip4_string(),
                        dcmd=node.command if node.command else None,
                        dimage=f"{node.name}",
                        prefixLen=node.node.get_ip4_prefixlen())
                nodemap[hash(node)] = n
        # Add links b/w the components of the network
        for e in nx_graph.edges():
            edge = nx_graph.edges[e]["relationship"]
            if isinstance(edge, howlitbe.topology.PhysicalLink):
                node1 = edge.node1
                node2 = edge.node2
                tired.logging.debug("Creating physical link between", node1.get_summary(), "and", node2.get_summary())
                netlink = net.addLink(nodemap[hash(node1)], nodemap[hash(node2)])
                nodemap[hash(edge)] = netlink  # JIC
        # Add links b/w docker containers, and switches
        # Get a list of connected switches
        for i in nx_graph.nodes():
            container = nx_graph.nodes[i]["data"]
            if isinstance(container, howlitbe.topology.Container):
                for n in nx.node_connected_component(nx_graph, hash(container.node)):
                    switch = nx_graph.nodes[n]["data"]
                    if isinstance(switch, howlitbe.topology.Switch):
                        # We've got deployment relation, skip
                        continue
                    tired.logging.debug("Adding link between container",
                            container.get_string_id(),
                            "and switch #",
                            str(switch.get_id()))
                    net.addLink(nodemap[hash(container)], nodemap[hash(switch)])

        return net


def run_topology(topology: howlitbe.topology.Topology):
    """
    Translates a given topology into containernet topology
    TODO: add limits (cpu, net, mem)
    """
    net = DeploymentBuilder().build_from_topology(topology)
    net.start()


def log_network_summary(net):
    from itertools import chain
    if HWL_DRY_RUN:
        tired.logging.warning("Unable to print network summary, containernet mock is used")
        return
    for o in chain(net.hosts, net.switches, net.controllers, net.links):
        if isinstance(o, Link):
            tired.logging.info("Link", str(o))
        elif isinstance(o, Node):
            interfaces = o.intfs.values()
            tired.logging.info("Node", o.name,
                    "with interfaces",
                    ', '.join(map(lambda i: f"{i.name} ({i.ip})", interfaces)))


def test_run_topology():
    topology = howlitbe.topology.Topology.new_topology_lb22_overlay(n_switches_total=1,
            n_gates=1,
            n_nodes=2,
            images_count={
                "image 1": 2,
            },
            n_overlays=2,
            image_commands={"image 1": "echo wazzup, man"})
    howlitbe.mininet.run_topology(topology=topology)
