"""
The application runs a set of simulations, analyzes network performance,
and generates (comparative) statistics.
"""

import howlitbe.scenario.lb22
import howlitbe.topology.Topology
import argparse
import tired.logging


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=str, choices=["replication"], default="replication", help="Select network scenario for simulation and optimization")
    p = parser.parse_args()
    return p


def main():
    args = _parse_arguments()

    # Generate arbitrary network topology
    topology = howlitbe.topology.Topology.new_topology(n_switches_total=4,
            n_gates=1,
            n_nodes = 16,
            images_count={
                "database": 12,
                "long-processing": 50,
                "short-processing": 200
            },
            n_overlays=10)


    if args.scenario == "replication":
        vnt = howlitbe.scenario.lb22.VirtualizedNetworkTechnology.new_replication_scenario()
