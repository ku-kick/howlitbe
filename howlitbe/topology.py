import dataclasses


class _Enumeration:
    """
    Enables derived instances to be have a hashable unique identifier. Each hash
    is unique within a class, hashes may repeat between classes.
    """

    __bound = dict()

    def __init__(self):
        """
        objtype - type of the object
        """
        if self.__class__.__name__ not in _Enumeration.__bound:
            _Enumeration.__bound[self.__class__.__name__] = 0

        self.__identifier = _Enumeration.__bound[self.__class__.__name__]
        _Enumeration.__bound[self.__class__.__name__] += 1

    def __hash__(self):
        return self.__identifier


class Node(_Enumeration):
    """
    Base class for network's node
    """
    pass
    def __init__(self, cpufrac: float = None):
        """
        cpufrac: fraction of overall CPU time for a particular host. [NOUNIT], fraction value.
        If None, no limit is used
        """
        _Enumeration.__init__(self)
        self.cpufrac = cpufrac  # Mininet (hence containernet too) allows setting CPU time fraction through utilizing linux CFS (https://www.kernel.org/doc/html/latest/scheduler/sched-design-CFS.html). See "mininet", CPULimitedHost, and "setCPUFrac()" (https://mininet.org/api/classmininet_1_1node_1_1CPULimitedHost.html)


class PhysicalLink(_Enumeration):
    """ Physical connection between nodes """

    def __init__(self, node1: Node, node2: Node, bandwidth: int):
        """
        bandwidth: max network bandwidth, [b/s]. TODO: re-check units, how it is implemented in the containernet itself.
        """
        self.node1 = node1  # Endpoint 1
        self.node2 = node2  # Endpoint 2
        self.bps = bandwidth  # Mininet (hence containernet too) allows setting bandwidth for a link. See "--bw" option.
        _Enumeration.__init__(self)


class Container(_Enumeration):
    """
    Container a running on a physical node
    """
    def __init__(self, node: Node, cpufrac: float, networkfrac: float, hddfrac: float):
        """
        cpufrac: scaled max. allowed CPU value from 0 to 1. [NOUNIT], fraction
        networkfrac: scaled max. allowed network bandwidth. [NOUNIT], fraction
        hddfrac: scaled max. fraction of bandwidth when accessing storage devices. [NOUNIT], fraction
        """
        self.node = node  # Node which the container is running on
        self.cpufrac = cpufrac  # Docker allows setting cpu limits. See --cpu-quota, --cpu-period, --cpu-shares. See https://docs.docker.com/engine/containers/resource_constraints/#configure-the-default-cfs-scheduler
        self.networkfrac = networkfrac  # Docker does not allow setting network bandwidth. However, it is possible through tc command, see `man tc (RATES)`, and https://stackoverflow.com/questions/25497523/how-can-i-rate-limit-network-traffic-on-a-docker-container
        self.hddfrac = cddfrac  # Docker allows limiting access for a particular piece of block device, virtualized, or otherwise. See --device-read-bps, https://stackoverflow.com/questions/36145817/how-to-limit-io-speed-in-docker-and-share-file-with-system-in-the-same-time
        _Enumeration.__init__(self)


def test_enumeration():
    import tired.logging
    tired.logging.info("Test whether the enumeration works for an instance that is derived from it")
    n1 = Node()
    n2 = Node()
    tired.logging.debug("Created nodes w/ ids", str(hash(n1)), str(hash(n2)))
    pl = PhysicalLink(n1, n2, 0.5)
    tired.logging.debug("id for", pl.__class__.__name__, "is", str(hash(pl)))
    # TODO: test container
    assert(hash(pl) == 0)
