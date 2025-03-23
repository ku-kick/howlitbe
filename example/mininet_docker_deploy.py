"""
Generates a simple topology, and deploys it on a containernet network
"""

import time
from mininet.cli import CLI
from mininet.log import setLogLevel
import howlitbe.mininet
import howlitbe.topology
import mininet.net
import mininet.node
import pathlib
import tired.logging
import os
import tired.command


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
    hosts = [h1, h2]
    for i in range(2):
        mountname = f'/tmp/mininet-{i}-mount'
        tired.command.execute(f'sudo rm -rf {mountname}')
        tired.command.execute(f'sudo mkdir -p {mountname}')
        tired.logging.info(f'For host "{hosts[i].name}: mounting {mountname} to /var')
        hosts[i].sendCmd(f'sudo mount --bind {mountname} /var')
        hosts[i].waitOutput()
        tired.logging.info(f"Launching containerd on {hosts[i].name}")
        hosts[i].sendCmd('containerd &')
        hosts[i].waitOutput()
        tired.logging.info(f"Launching containerd on {hosts[i].name}")
        time.sleep(3) # Crutch: containerd needs some time to launch
        tired.logging.info(f"Deploying Docker on {hosts[i].name}")
        hosts[i].sendCmd('dockerd &')
        hosts[i].waitOutput()

    # Drop into Mininet shell
    tired.logging.info("Dropping into containernet shell")
    CLI(net)

    net.stop()


if __name__ == "__main__":
    main()
