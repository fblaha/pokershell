import time

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
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 6d 9d')
        result = self.simulator._simulate_river(-1, cards)
        self.assertTrue(result.win / result.total > 0.9)

    def test_turn(self):
        cards = model.Card.parse_cards_line('6s 8c 2h 8h 2c 3c')
        print(self.simulator.simulate(*cards))

    def test_turn_full_house(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac Jd')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result.win / result.total > 0.9)

    def test_turn_bad_luck(self):
        cards = model.Card.parse_cards_line('2c 4d 8c Js Qd Qc')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result.win / result.total < 0.2)


class TestMonteCarloSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.MonteCarloSimulator(5, 10000)

    def test_hole_cards(self):
        cards = model.Card.parse_cards_line('As 6c')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result.tie < result.win < result.lose)

    def test_sample(self):
        cards = model.Card.parse_cards_line('As 6c')
        result = self.simulator._sample(5000, tuple(cards))
        print(result)
        self.assertTrue(result.tie < result.win < result.lose)

    def test_avg_cmp_count(self):
        self.assertEqual(1, self.simulator._get_avg_eval_count(1))
        self.assertEqual(1.5, self.simulator._get_avg_eval_count(2))
        self.assertEqual(1.75, self.simulator._get_avg_eval_count(3))

    def test_avg_cmp_count_assignment(self):
        self.assertEqual(1, simulation.MonteCarloSimulator(2, 10000)._avg_eval_count)
        self.assertEqual(1.5, simulation.MonteCarloSimulator(3, 10000)._avg_eval_count)

    def test_river_full_house(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 6d 9d')
        result = self.simulator.simulate(*cards)
        print(result)
        self.assertTrue(result.win / result.total > 0.9)

    def test_calculator_comparison(self):
        cards = model.Card.parse_cards_line('4h 4d 8c 4c Qd')
        result = self.simulator.simulate(*cards)
        rate = result.win / result.total
        print(rate)
        self.assertTrue(0.75 <= rate <= 0.79)

    def test_performance(self):
        cards = model.Card.parse_cards_line('As Ah Ad 8s Ac 7d')
        start_time = time.time()
        simulation.MonteCarloSimulator(6, config.sim_cycles).simulate(*cards)
        elapsed_time = time.time() - start_time
        print('Elapsed time : %f' % elapsed_time)
        self.assertTrue(elapsed_time < 10)


class TestLookUpSimulator(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.LookUpSimulator(5)

    def test_not_suited(self):
        cards = model.Card.parse_cards_line('As 6c')
        result = self.simulator.simulate(*cards)
        self.assertEqual(19.21, result.win)

    def test_suited(self):
        cards = model.Card.parse_cards_line('Ac 6c')
        result = self.simulator.simulate(*cards)
        self.assertEqual(23.33, result.win)

    def test_pair(self):
        cards = model.Card.parse_cards_line('Ac Ad')
        result = self.simulator.simulate(*cards)
        self.assertEqual(55.78, result.win)


class TestSimulatorManager(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.manager = simulation.SimulatorManager()
        self._player_num = config.player_num

    def tearDown(self):
        config.player_num = self._player_num
        return super().tearDown()

    def test_preflop(self):
        cards = model.Card.parse_cards_line('Ac 6c')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.LookUpSimulator)

    def test_flop(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.MonteCarloSimulator)

    def test_turn(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.BruteForceSimulator)

    def test_river(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d 5h')
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.BruteForceSimulator)

    def test_river_five_players(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d 5h')
        config.player_num = 5
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.MonteCarloSimulator)

    def test_turn_seven_players(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d')
        config.player_num = 7
        simulator = self.manager.find_simulator(*cards)
        self.assertIsInstance(simulator, simulation.MonteCarloSimulator)
