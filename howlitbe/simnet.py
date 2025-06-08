"""
Describes network as a set of agents which either decide to pass a request to
one of its neighbors, or process it.
"""

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
import dataclasses
import howlitbe.topology
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import tired.logging


class NodeAgent:

    def __init__(self, topology, inode, user_constructor_arg):
        """
        Each instance will be provided w/ `user_constructor_arg` The way it's
        used is up to a particular implementation
        """
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


class RandomPassNodeAgent(NodeAgent):

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
    """
    Engine. On each step, provides agents w/ a lot of available information,
    so they make a decision on how much information they can process w/ over
    delta-t time.
    """

    def __init__(self, network_topology: howlitbe.topology.Topology,
                node_agent_type: NodeAgent, user_arg):
        """
        `user_arg` - implementation-defined argument that is used during
        object construction
        """
        self.topology = network_topology
        self.agent_type = node_agent_type
        self.previous_time = 0.0
        self.pending_data: list[_PendingData] = list()

        # Initialize agents
        self.agent_index = dict()
        for inode in self.topology.as_nxgraph().nodes:
            self.agent_index[inode] = self.agent_type(self.topology,
                    inode, user_arg)

    def get_previous_time(self):
        """
        "Current" time, i.e. before delta-t increment
        """
        return self.previous_time

    def transfer(node1: int, node2: int, )

    def step(self, dt, user_arg):
        """
        `user_arg` -- gets passed as a custom argument to all agent nodes that
        are subject to data processing.
        POST: `get_previous_time` is incremented by `delta-t`
        """
        # Generate inbound traffic
        for inode in self.topology.as_nxgraph().nodes:
            node_object = self.topology.as_nxgraph().nodes[hash(inode)]["data"]
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

        # Process pending data
        new_pending_data = list()
        for pd in self.pending_data:
            agent_object: NodeAgent = self.agent_index[pd.deciding_inode]
            if isinstance(pd.deciding_inode, howlitbe.topology.Switch):
                # Get neighboring nodes excluding those from backtrace
                neighbor_nodes = [i for i in \
                        self.topology.as_nxgraph().neighbors(hash(pd.deciding_inode))
                        if hash(i) not in map(hash,
                        pd.backtrace_nodes_as_node_objects)]

                neighbor_agents = [self.agent_index[i] for i in neighbor_nodes]
                neighbor_links = [
                        self.topology.as_nxgraph() \
                        .get_edge_data(hash(pd.deciding_inode), hash(i))["data"] \
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
                pd.deciding_inode = neighbor_nodes[hash(inext)]
                new_pending_data.append(pd)
                # TODO save for the stat
            elif isinstance(pd.deciding_inode, howlitbe.topology.Node):
                neighbor_agents = [self.agent_index[i] for i in \
                        self.topology.as_nxgraph().neighbors(pd.deciding_inode)]
                neighbor_nodes = [i for i in \
                        self.topology.as_nxgraph().neighbors(hash(pd.deciding_inode))]
                neighbor_links = [self.topology.edges([hash(pd.deciding_inode)])]
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

    def run(self, dt, user_arg, t1):
        """
        `dt` - simulation step [s]
        `user_arg` - custom user argument
        `t1` - sim. duration [s]
        """
        while self.previous_time < t1:
            self.step(dt, user_arg)


class SimTraceApp:
    """
    Small application for debugging / rendering the simulation.
    """
    def __init__(self,
                simulation: Simulation,
                topology: howlitbe.topology.Topology,
                user_arg):
        self.simulation = simulation
        self.topology = topology
        self.user_arg=user_arg

        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.geometry("1200x600")
        self.root.title("SimTrace")

        # Frame for the plot
        self.frame = ctk.CTkFrame(master=self.root, fg_color="darkblue")
        self.frame.place(relx=0.33, rely=0.025, relwidth=0.66, relheight=0.95)

        # Button to update the plot
        self.button = ctk.CTkButton(master=self.root, text="Step",
                command=self.on_step)
        #self.button.place(relx=0.025, rely=0.25, width=300, height=50)
        self.button.place(relx=0.025, rely=0.25, relheight=0.04)

        # TODO: process
        self.button = ctk.CTkButton(master=self.root, text="Run",
                command=self.update_plot)
        #self.button.place(relx=0.025, rely=0.25, width=300, height=50)
        self.button.place(relx=0.025, rely=0.30, relheight=0.04)

        # Entry for number of points
        self.input = ctk.CTkEntry(master=self.root, placeholder_text="dt",
                width=300, height=50)
        self.input.place(relx=0.025, rely=0.35)

        self.current_t = ctk.CTkLabel(master=self.root,
                text=f"Current time: {simulation.get_previous_time()}")
        self.current_t.place(relx=0.025, rely=0.45)

        # Initial plot
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        self.update_plot()  # Initial plot

    def run(self):
        self.root.mainloop()

    def on_step(self):
        self.simulation.step(float(self.input.get()), self.user_arg)
        self.update_plot()
        self.update_ui()

    def update_plot(self):
        self.topology.render(ax=self.ax, show=False)

    def update_ui(self):
        self.current_t.configure(text=f"Current time: {self.simulation.get_previous_time()}")

    def update_plot_legacy(self):
        # Clear the previous plot
        self.ax.clear()

        # Get number of points from input
        num_points = int(self.input.get()) if self.input.get().isdigit() else 100
        sizes = self.slider.get()

        # Generate random data
        x = np.random.rand(num_points)
        y = np.random.rand(num_points)
        self.ax.scatter(x, y, s=sizes, c='blue', alpha=0.5)

        # Update the plot
        self.ax.axis("off")
        self.canvas.draw()



def test_inbound_passing_w_termination():
    """ pass the request among nodes, terminate, if dead end"""
    pass
    # TODO: sketch a simple network, test a test (random) agent
    s1 = howlitbe.topology.Switch(is_gate=True)
    s2 = howlitbe.topology.Switch(is_gate=False)
    s3 = howlitbe.topology.Switch(is_gate=False)
    n1 = howlitbe.topology.Node()
    n2 = howlitbe.topology.Node()
    n3 = howlitbe.topology.Node()
    n4 = howlitbe.topology.Node()
    topology = howlitbe.topology.Topology(nx.Graph())
    topology.add_edge(s1, s2, howlitbe.topology.PhysicalLink(s1, s2, bandwidth=1024))
    topology.add_edge(s1, s3, howlitbe.topology.PhysicalLink(s1, s3, bandwidth=1024))
    topology.add_edge(s1, n1, howlitbe.topology.PhysicalLink(s1, n1, bandwidth=512))
    topology.add_edge(s1, n2, howlitbe.topology.PhysicalLink(s1, n2, bandwidth=512))
    topology.add_edge(s3, n3, howlitbe.topology.PhysicalLink(s2, n3, bandwidth=512))
    topology.add_edge(s3, n4, howlitbe.topology.PhysicalLink(s2, n4, bandwidth=512))
    topology.graph.edges[(hash(s1), hash(n1))]["label"] = "Hi"
    simulation = Simulation(topology,
            RandomPassNodeAgent,
            None)
    simapp = SimTraceApp(simulation=simulation,
            topology=topology,
            user_arg=None)
    simapp.run()

    if False:
        topology.render()
        simulation.run()
