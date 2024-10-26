import os
import random
import tired.logging


_generated_seed = False
"""
"Do-once" flag for random generators
"""


def random_uniform(from_inclusive: float, to_exclusive: float):
    """
    if no HWL_RND_SEED value specified, seeds the twister w/ a truly random
    number (ONLY once), and generates a random number in the range
    [from_inclusive, to_exclusive).
    """
    global _generated_seed

    # Make sure seed value is generated
    if not _generated_seed:
        # Generate 4 random bytes from os' RNG source
        seed = os.urandom(4)
        seed = int(seed[0]) << 24 | int(seed[1]) << 16 | int(seed[2]) << 8 | int(seed[3])
        # Check if user provided the seed
        seed = os.getenv("HWL_RND_SEED", seed)
        tired.logging.info(f"Environment variable HWL_RND_SEED={seed} (Initial value for RNG)")
        # Reset seed value
        random.seed(seed)
        _generated_seed = True

    # Proceed to actual RNG
    return random.uniform(from_inclusive, to_exclusive)
