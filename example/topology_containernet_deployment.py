"""
Generates a simple topology, and deploys it on a containernet network
"""

from mininet.cli import CLI
from mininet.log import setLogLevel
import howlitbe.containernet
import howlitbe.topology
import tired.logging


def main():
    setLogLevel('debug')
    tired.logging.set_level(tired.logging.DEBUG)
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
    net.start()
    howlitbe.containernet.log_network_summary(net)
    CLI(net)


if __name__ == "__main__":
    main()
