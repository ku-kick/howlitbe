import howlitbe.topology


class Simulation:
    def __init__(self) -> None:
        pass


def test_simnet_basic_deployment():
    topology = howlitbe.topology.Topology.new_topology_lb22_overlay(n_switches_total=4,
            n_gates=1,
            n_nodes = 16,
            images_count={
                "database": 12,
                "long-processing": 50,
                "short-processing": 200
            },
            n_overlays=10)
    simunation = Simulation()

