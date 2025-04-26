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


H1_CONTAINER_NAME = "docker_simple_http_server"
H2_CONTAINER_NAME = "docker_simple_http_client"


def main():
    # Save containers into a certain directory, so they can be ported by the deployed containers
    # TODO: add "already exists" check
    image_tar_output_dir = '/tmp/dockerimages'
    tired.command.execute(f'mkdir -p {image_tar_output_dir}')
    tired.command.execute(f'docker save -o {image_tar_output_dir}/{H1_CONTAINER_NAME} {H1_CONTAINER_NAME}')
    tired.command.execute(f'docker save -o {image_tar_output_dir}/{H2_CONTAINER_NAME} {H2_CONTAINER_NAME}')
    
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
    h2.setIP("10.0.0.4")
    # Get network summary
    # howlitbe.mininet.log_network_summary(net)

    # Deploy docker in the network namespaces of hosts h1, and h2
    deployscriptpath = pathlib.Path(__file__).resolve().parent / "docker-deploy-debian.sh"
    hosts = [h1, h2]
    for i in range(2):
        mountname = f'/tmp/mininet-{i}-mount'
        tired.command.execute(f'sudo rm -rf {mountname}')
        tired.command.execute(f'sudo mkdir -p {mountname}')

        # Bind var/ to sandbox docker instance
        tired.logging.info(f'For host "{hosts[i].name}: mounting {mountname} to /var')
        hosts[i].sendCmd(f'sudo mount --bind {mountname} /var')
        hosts[i].waitOutput()

        # Bind container images' directory for being used by running docker instances
        hosts[i].sendCmd(f'mkdir -p /var/dockerimages && mount --bind {image_tar_output_dir} /var/dockerimages')
        hosts[i].waitOutput()

        tired.logging.info(f"Launching containerd on {hosts[i].name}")
        hosts[i].sendCmd(f'containerd --log-level debug > /tmp/mininet-containerd-{i}.log 2>&1 &')
        hosts[i].waitOutput()

        tired.logging.info(f"Launching containerd on {hosts[i].name}")
        time.sleep(3) # TODO Crutch: containerd needs some time to launch
        tired.logging.info(f"Deploying Docker on {hosts[i].name}")
        hosts[i].sendCmd(f'dockerd --log-level debug > /tmp/mininet-dockerd-{i}.log 2>&1 &')
        hosts[i].waitOutput()

        # Load canned docker images
        time.sleep(3) # TODO Crutch: dockerd needs some time to launch
        hosts[i].sendCmd(f'docker load -i /var/dockerimages/{H1_CONTAINER_NAME}')
        hosts[i].waitOutput()
        hosts[i].sendCmd(f'docker load -i /var/dockerimages/{H2_CONTAINER_NAME}')
        hosts[i].waitOutput()

    # Drop into Mininet shell
    tired.logging.info("Dropping into containernet shell")
    CLI(net)

    net.stop()


if __name__ == "__main__":
    main()
