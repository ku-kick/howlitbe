#!/usr/bin/python3

"""
Let a - leaves per node, L - number of hops, N - total number of nodes in the tree

Therefore, N = a**0 + a**1 + a**2 + ... + a**L

a = floor((N - 1) ** (1 / L))
a <= floor(N ** (1 / L))
"""


import math


def count_nodes(n_hops, n_nodes_per_hop):
    nodes_total = 0
    for i in range(n_hops + 1):
        nodes_total += n_nodes_per_hop ** i

    return nodes_total


def main():
    print("hops, nodes per hop, nodes max, nodes max ** (1 / hops), ceil(npsq) >= nodes per hop")

    for hops in range(1, 100):
        for nodesph in range(1, 100):  # Nodes per hop in the tree
            nodes_total = count_nodes(hops, nodesph)
            #approx = (nodes_total - 1) ** (1 / hops)
            print(nodesph <= math.floor((nodes_total) ** (1 / hops)))
            print(nodesph == int(math.floor((nodes_total - 1) ** (1 / hops))))

if __name__ == "__main__":
    main()
