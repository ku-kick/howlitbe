"""
Deploys docker inside mininet hosts
"""

import mininet
import mininet.node
import pathlib


def deploy_docker(host: mininet.node.Host, net: mininet.Mininet):
    scriptpath = pathlib.Path(__file__).resolve().parent / "res" / "docker-deploy-debian.sh"
    host.cmd(f"unshare --mount '/bin/bash {scriptpath} &")
