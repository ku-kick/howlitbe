#!/usr/bin/python3
import networkx as nx
import howlitbe.topology


def main():
    pass

if __name__ == "__main__":
    g = nx.Graph()
    n1 = howlitbe.topology.Node()
    n2 = howlitbe.topology.Node()
    n3 = howlitbe.topology.Node()
    g.add_node(n1, data=n1)
    g.add_node(n2, data=n2)
    g.add_node(n3, data=n3)
    g.add_edge(n1, n2, weight=3, data=howlitbe.topology.PhysicalLink(n1, n2, 10))
    g.add_edge(n2, n3, data=howlitbe.topology.PhysicalLink(n2, n3, 10))
    print(g.nodes)
    print(g.nodes[n1])
    for inode in g.nodes:
        print(inode)
    print(g.edges(n2, n1))
    print(g.get_edge_data(n2, n1))
