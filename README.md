# Howlitbe

Containernet-driven simulation environment for running Monte-Carlo simulations
on close-to-real networks without the need for top-notch hardware. PITA-free
approach to testing your shiny SDN balancers, ingress-balancing algorithms, and
whatnot.

# Mission statement

**2024-10: I NEED TO CONCOCT A WELL-DOCUMENTED TOOL FOR FAST AND RELIABLE
VALIDATION OF MY MODEL (IN ITS CURRENT FORM, WITHOUT ANY ALTERATIONS), IN THE
SHORTEST POSSIBLE AMOUNT OF TIME, SO I WILL BE ABLE TO WRITE A PAPER THAT WILL
BECOME THE CORE OF MY RESEARCH.**

Therefore:

1. "howlitbe" IS mostly applicable to the model I mentioned. "howlitbe" MAY BE, but DOES NOT NEED TO BE extendable;
2. "howlitbe" MAY NOT be well maintained in the second half of 2025;

# WTFaQ

**Running from venv**

```bash
su
python3 -m venv ./venv --system-site-packages
pip install .

# ???
# PROFIT!
```

# Installation

- Make sure Mininet is installed on your (virtual) machine;
- run `cd tools ; ./mininet-postinstall.sh` to complete your installation w/ Docker, and whatever dependencies there are;
