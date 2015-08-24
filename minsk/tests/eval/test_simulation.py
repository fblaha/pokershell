import testtools

import minsk.eval.simulation as simulation
import minsk.tests.eval.common as common


class TestBruteForceSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.BruteForceSimulator()

    def test_brute_force_turn(self):
        cards = self.parse_cards('6s 8c 2h 8h 2c 3c')
        print(self.simulator.simulate(*cards))
