from __future__ import annotations

import unittest
from pathlib import Path

from benchmarks import tree_discriminator_validation as discriminator
from benchmarks import tree_validation as validation


HERE = Path(__file__).resolve().parent


class TreeDiscriminatorTests(unittest.TestCase):
    def test_cases_match_local_topology(self) -> None:
        topology = validation.load_topology(HERE / "tree_topology.json")
        discriminator.self_test(topology)


if __name__ == "__main__":
    unittest.main()
