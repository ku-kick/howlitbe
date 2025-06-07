"""
Describes network as a set of agents which either decide to pass a request to
one of its neighbors, or process it.
"""

import dataclasses
import howlitbe.topology
import networkx as nx
import random
import tired.logging


class NodeAgent:

    def __init__(self, topology, inode):
        tired.logging.info(f"Generated node agent for node {inode}")
        pass

    def get_next_hop(self,
                simulation,
                topology: howlitbe.topology.Topology,
                neighbors_as_agents: list, # Neighbors represented as NodeAgent objects
                neighbors_as_node_objects: list, # Neighbors represented as howlitbe.topology.Node objects
                neighboring_physical_links: list[howlitbe.topology.PhysicalLink], # Physical links to neighbors
                self_as_node_object: howlitbe.topology.Node,
                dt,
                user_arg=None) -> int:
        """
        Returns index for the next hop, as listed in `neighbors_as_agents`,
        or `neighbors_as_node_objects`:
        """
        raise NotImplemented()

    def calc_processed_data_amnt_bytes(self,
                simulation,
                topology: howlitbe.topology.Topology,
                neighbors_as_agents: list, # Neighbors represented as NodeAgent objects
                neighbors_as_node_objects: list, # Neighbors represented as howlitbe.topology.Node objects
                neighboring_physical_links: list[howlitbe.topology.PhysicalLink], # Physical links to neighbors
                self_as_node_object: howlitbe.topology.Node,
                dt,
                data_amt,
                user_arg=None) -> float:
        return data_amt

    def generate_inbound_data(self,
                simulation,
                topology: howlitbe.topology.Topology,
                self_as_node_object: howlitbe.topology.Node,
                dt,
                user_arg=None) -> float:
        raise NotImplemented()


class RandomPassTestNodeAgent(NodeAgent):

    def __init__(self, topology, inode):
        super().__init__(topology, inode)

    def generate_inbound_data(self, simulation, topology, self_as_node_object,
                dt, user_arg=None):
        return 1.0 * dt

    def calc_processed_data_amnt_bytes(self,
                simulation,
                topology: howlitbe.topology.Topology,
                neighbors_as_agents: list, # Neighbors represented as NodeAgent objects
                neighbors_as_node_objects: list, # Neighbors represented as howlitbe.topology.Node objects
                neighboring_physical_links: list[howlitbe.topology.PhysicalLink], # Physical links to neighbors
                self_as_node_object: howlitbe.topology.Node,
                dt,
                data_amt,
                user_arg=None):
        return data_amt * 0.995

    def get_next_hop(self,
                simulation,
                topology: howlitbe.topology.Topology,
                neighbors_as_agents: list, # Neighbors represented as NodeAgent objects
                neighbors_as_node_objects: list, # Neighbors represented as howlitbe.topology.Node objects
                neighboring_physical_links: list[howlitbe.topology.PhysicalLink], # Physical links to neighbors
                self_as_node_object: howlitbe.topology.Node,
                dt,
                user_arg=None):
        return random.randrange(0, len(neighbors_as_agents))


@dataclasses.dataclass
class _PendingData:
    deciding_inode: object
    backtrace_nodes_as_agents: list
    backtrace_nodes_as_node_objects: list
    data_amount_bytes: float


class Simulation:

    def __init__(self, network_topology: howlitbe.topology.Topology,
                node_agent_type: NodeAgent):
        self.topology = network_topology
        self.agent_type = node_agent_type
        self.previous_time = 0.0
        self.pending_data: list[_PendingData] = list()

        # Initialize agents
        self.agent_index = dict()
        for inode in self.topology.as_nxgraph().nodes:
            self.agent_index[inode] = self.agent_type(self.topology,
                    inode)

    def get_previous_time(self):
        return self.previous_time

    def step(self, dt, user_arg):
        # Generate inbound traffic
        for inode in self.topology.as_nxgraph().nodes:
            node_object = self.topology.as_nxgraph().nodes[inode]["data"]
            if isinstance(node_object, howlitbe.topology.Switch) \
                        and node_object.is_gate:
                data_amount = self.agent_index[inode].generate_inbound_data(
                        self,
                        self.topology,
                        node_object,
                        dt,
                        user_arg)
                self.pending_data.append(_PendingData(
                        deciding_inode=inode,
                        backtrace_nodes_as_agents=list(),
                        backtrace_nodes_as_node_objects=list(),
                        data_amount_bytes=data_amount))
                        # backtrace_nodes_as_agents=[self.agent_index[inode]],
                        # backtrace_nodes_as_node_objects=[inode],

        # Process pending data
        new_pending_data = list()
        for pd in self.pending_data:
            agent_object: NodeAgent = self.agent_index[pd.deciding_inode]
            if isinstance(pd.deciding_inode, howlitbe.topology.Switch):
                # Get neighboring nodes excluding those from backtrace
                neighbor_nodes = [i for i in \
                        self.topology.as_nxgraph().neighbors(pd.deciding_inode)
                        if hash(i) not in map(hash,
                        pd.backtrace_nodes_as_node_objects)]

                neighbor_agents = [self.agent_index[i] for i in neighbor_nodes]
                neighbor_links = [
                        self.topology.as_nxgraph() \
                        .get_edge_data(pd.deciding_inode, i)["data"] \
                        for i in neighbor_nodes]
                inext = agent_object.get_next_hop(
                        self,
                        self.topology,
                        neighbor_agents,
                        neighbor_nodes,
                        neighbor_links,
                        agent_object,
                        user_arg)
                pd.backtrace_nodes_as_agents.append(
                        self.agent_index[pd.deciding_inode])
                pd.backtrace_nodes_as_node_objects.append(pd.deciding_inode)
                pd.deciding_inode = neighbor_nodes[inext]
                new_pending_data.append(pd)
                # TODO save for the stat
            elif isinstance(pd.deciding_inode, howlitbe.topology.Node):
                # TODO: process data
                neighbor_agents = [self.agent_index[i] for i in \
                        self.topology.as_nxgraph().neighbors(pd.deciding_inode)]
                neighbor_nodes = [i for i in \
                        self.topology.as_nxgraph().neighbors(pd.deciding_inode)]
                neighbor_links = [self.topology.edges([])]
                processed_amnt = agent_object.calc_processed_data_amt_bytes(
                        self,
                        self.topology,
                        neighbor_agents,
                        neighbor_nodes,
                        neighbor_links,
                        agent_object,
                        dt,
                        pd.data_amount_bytes,
                        user_arg)
                # TODO: save for the stat
            else:
                raise TypeError(f"Unsupported type {pd.__class__}")
        self.pending_data = new_pending_data

        self.previous_time += 1


def test_inbound_passing_w_termination():
    """ pass the request among nodes, terminate, if dead end"""
    pass
    # TODO: sketch a simple network, test a test (random) agent
