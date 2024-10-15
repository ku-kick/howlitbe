"""
Applies request balancing rules: which node should perform which request.
"""

import howlitbe.topology

class Base:
    "Base ingress interface"

    def __init__(topology: howlitbe.topology.Topology):
        self._topology = topology  # Represents network topology

    def get_request_processor(self, request: bytes) -> howlitbe.topology.Node:
        """
        Applies routing strategy to forward ingress request to a particular processing node
        Returns processing node descriptor
        """
        raise NotImplemented()

