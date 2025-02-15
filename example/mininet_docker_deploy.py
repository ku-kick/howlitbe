"""
Generates a simple topology, and deploys it on a containernet network
"""

from mininet.cli import CLI
from mininet.log import setLogLevel
import howlitbe.mininet
import howlitbe.topology
import mininet.net
import mininet.node
import pathlib
import tired.logging


def main():
    setLogLevel('debug')
    tired.logging.set_level(tired.logging.DEBUG)

    # Build the basic network topology
    net = mininet.net.Mininet(controller=mininet.node.Controller)
    c1 = net.addController("c0")
    s1 = net.addSwitch("s1")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    lh1s1 = net.addLink(h1, s1)
    lh2s1 = net.addLink(h2, s1)
    lc1s1 = net.addLink(c1, s1)

    # Run the network
    tired.logging.info("starting the network")
    net.start()
    # Get network summary
    howlitbe.mininet.log_network_summary(net)

    # Deploy docker in the network namespaces of hosts h1, and h2
    deployscriptpath = pathlib.Path(__file__).resolve().parent / "res" / "docker-deploy-debian.sh"
    cmd = f'unshare --croup --mount /bin/bash {deployscriptpath}&'
    h1.sendCmd()

    # Drop into Mininet shell
    tired.logging.info("Dropping into containernet shell")
    CLI(net)


if __name__ == "__main__":
    main()
