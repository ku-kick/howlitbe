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
import os


def main():
    os.system('cgroupfs-umount')
    os.system('cgroupfs-mount')

    setLogLevel('debug')
    tired.logging.set_level(tired.logging.DEBUG)

    # Build the basic network topology
    net = mininet.net.Mininet(controller=mininet.node.Controller, switch=mininet.node.OVSSwitch, waitConnected=True)
    c1 = net.addController("c1", port=6633)
    s1 = net.addSwitch("s1")
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    lh1s1 = net.addLink(s1, h1)
    lh2s1 = net.addLink(s1, h2)

    # Run the network
    tired.logging.info("starting the network")
    net.build()
    net.start()
    c1.start()
    s1.start([c1])
    # Get network summary
    # howlitbe.mininet.log_network_summary(net)

    # Deploy docker in the network namespaces of hosts h1, and h2
    deployscriptpath = pathlib.Path(__file__).resolve().parent / "docker-deploy-debian.sh"

    cmd = f'unshare --mount --pid --fork /bin/bash {deployscriptpath} 1&'
    tired.logging.info(f"Deploying Docker on h1")
    h1.sendCmd(cmd)

    cmd = f'unshare --mount --pid --fork /bin/bash {deployscriptpath} 2&'
    tired.logging.info(f"Deploying Docker on h2")
    h2.sendCmd(cmd)

    # Drop into Mininet shell
    tired.logging.info("Dropping into containernet shell")
    CLI(net)

    net.stop()


if __name__ == "__main__":
    main()
