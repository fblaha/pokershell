import testtools

import minsk
import minsk.eval.simulation as simulation
import minsk.tests.eval.common as common


class TestBruteForceSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = minsk.eval.simulation.BruteForceSimulator()

    def test_brute_force(self):
        cards = self.parse_cards('6s 8c 2h 8h 2c 3c Jd')
        self.simulator.simulate(*cards)
