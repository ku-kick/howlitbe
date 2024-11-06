"""
Generates a simple topology, and deploys it on a containernet network
"""

import howlitbe.containernet
import howlitbe.topology
from mininet.cli import CLI


def main():
    # Overlay topology like the one described in the '22 paper
    topology = howlitbe.topology.Topology.new_topology_lb22_overlay(n_switches_total=1,
            n_gates=1,
            n_nodes=2,
            images_count={
                "test_server:latest": 1,
                "test_client:latest": 1,
            },
            n_overlays=2)
    net = howlitbe.containernet.DeploymentBuilder().build_from_topology(topology=topology)
    howlitbe.containernet.log_network_summary(net)
    net.start()
    CLI(net)


if __name__ == "__main__":
    main()
