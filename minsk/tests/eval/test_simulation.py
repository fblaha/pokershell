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

    def test_full_house(self):
        cards = self.parse_cards('As 6c Ad 8s Ac 6d')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result[0] / sum(result) > 0.9)

    def test_bad_luck(self):
        cards = self.parse_cards('2c 4d 8c Js Qd Qc')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result[0] / sum(result) < 0.2)
