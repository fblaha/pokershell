import testtools

import minsk.config as config

import minsk.eval.simulation as simulation
import minsk.model as model
import minsk.tests.eval.common as common


class TestBruteForceSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.BruteForceSimulator()

    def test_river_full_house(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac 6d 9d')
        result = self.simulator.simulate_river(*cards)
        self.assertTrue(result[0] / sum(result) > 0.9)

    def test_turn(self):
        cards = model.Card.parse_cards('6s 8c 2h 8h 2c 3c')
        print(self.simulator.simulate(*cards))

    def test_turn_full_house(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac Jd')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result[0] / sum(result) > 0.9)

    def test_turn_bad_luck(self):
        cards = model.Card.parse_cards('2c 4d 8c Js Qd Qc')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result[0] / sum(result) < 0.2)


class TestMonteCarloSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.MonteCarloSimulator(2, 1000)

    def test_river_full_house(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac 6d 9d')
        result = self.simulator.simulate_river(*cards)
        print(result)
        self.assertTrue(result[0] / sum(result) > 0.9)


class TestPreFlopSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.PreFlopSimulator(5)

    def test_not_suited(self):
        cards = model.Card.parse_cards('As 6c')
        result = self.simulator.simulate(*cards)
        self.assertEqual(19.21, result[0])

    def test_suited(self):
        cards = model.Card.parse_cards('Ac 6c')
        result = self.simulator.simulate(*cards)
        self.assertEqual(23.33, result[0])

    def test_pair(self):
        cards = model.Card.parse_cards('Ac Ad')
        result = self.simulator.simulate(*cards)
        self.assertEqual(55.78, result[0])


class TestSimulatorManager(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.manager = simulation.SimulatorManager()
        self._player_num = config.player_num

    def tearDown(self):
        config.player_num = self._player_num
        return super().tearDown()

    def test_preflop(self):
        cards = model.Card.parse_cards('Ac 6c')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.PreFlopSimulator)

    def test_flop(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.MonteCarloSimulator)

    def test_turn(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac 4d')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.BruteForceSimulator)

    def test_river(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac 4d 5h')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.BruteForceSimulator)

    def test_river_five_players(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac 4d 5h')
        config.player_num = 5
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.MonteCarloSimulator)

    def test_turn_seven_players(self):
        cards = model.Card.parse_cards('As 6c Ad 8s Ac 4d')
        config.player_num = 7
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.MonteCarloSimulator)
