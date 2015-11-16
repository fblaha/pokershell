import time
import unittest

import pokershell.eval.simulation as simulation
import pokershell.model as model
import pokershell.tests.eval.common as common

monte_carlo = simulation.MonteCarloSimulator


class TestBruteForceSimulator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.BruteForceSimulator()

    def test_river_full_house(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 6d 9d')
        result = self.simulator._simulate_river(cards)
        self.assertTrue(result.win / result.total > 0.9)

    def test_turn(self):
        cards = model.Card.parse_cards_line('6s 8c 2h 8h 2c 3c')
        print(self.simulator.simulate(2, *cards))

    def test_turn_full_house(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac Jd')
        result = self.simulator.simulate(2, *cards)
        print(result)
        self.assertTrue(result.win / result.total > 0.9)

    def test_turn_bad_luck(self):
        cards = model.Card.parse_cards_line('2c 4d 8c Js Qd Qc')
        result = self.simulator.simulate(2, *cards)
        print(result)
        self.assertTrue(result.win / result.total < 0.2)


class TestMonteCarloSimulator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = monte_carlo(0.5)

    def test_hole_cards(self):
        cards = model.Card.parse_cards_line('As 6c')
        result = self.simulator.simulate(5, *cards)
        print(result)
        self.assertTrue(result.tie < result.win < result.lose)

    def test_sample(self):
        cards = model.Card.parse_cards_line('As 6c')
        result = self.simulator._sample(5, 0.5, tuple(cards))
        print(result)
        self.assertTrue(result.tie < result.win < result.lose)

    def test_river_full_house(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 6d 9d')
        result = self.simulator.simulate(5, *cards)
        print(result)
        self.assertTrue(result.win / result.total > 0.9)
        winning_hands = result.sorted_winning_hands
        self.assertEquals(1, len(winning_hands))
        self.assertEquals(model.Hand.FULL_HOUSE, winning_hands[0][0])
        self.assertEquals(result.win, winning_hands[0][1])

    def test_calculator_comparison(self):
        cards = model.Card.parse_cards_line('4h 4d 8c 4c Qd')
        result = self.simulator.simulate(5, *cards)
        rate = result.win / result.total
        print(rate)
        print(result)
        self.assertTrue(0.75 <= rate <= 0.8)

    def test_hand_stats(self):
        cards = model.Card.parse_cards_line('4h 4d 8c 4c Qd')
        result = self.simulator.simulate(5, *cards)
        print(result)
        self.assertEquals(result.win, sum(result.winning_hands))
        self.assertEquals(result.lose, sum(result.beating_hands))

    def test_performance(self):
        cards = model.Card.parse_cards_line('As Ah Ad 8s Ac 7d')
        start_time = time.time()
        monte_carlo(monte_carlo.sim_cycle.value).simulate(6, *cards)
        elapsed_time = time.time() - start_time
        print('Elapsed time : %f' % elapsed_time)
        self.assertTrue(elapsed_time < 10)


class TestLookUpSimulator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.simulator = simulation.LookUpSimulator()

    def test_not_suited(self):
        cards = model.Card.parse_cards_line('As 6c')
        result = self.simulator.simulate(5, *cards)
        self.assertEqual(19.21, result.win)

    def test_suited(self):
        cards = model.Card.parse_cards_line('Ac 6c')
        result = self.simulator.simulate(5, *cards)
        self.assertEqual(23.33, result.win)

    def test_pair(self):
        cards = model.Card.parse_cards_line('Ac Ad')
        result = self.simulator.simulate(5, *cards)
        self.assertEqual(55.78, result.win)


class TestSimulatorManager(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.manager = simulation.SimulatorManager()

    def test_preflop(self):
        cards = model.Card.parse_cards_line('Ac 6c')
        simulator = self.manager.find_simulator(5, *cards)
        self.assertIsInstance(simulator, simulation.LookUpSimulator)

    def test_flop(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac')
        simulator = self.manager.find_simulator(2, *cards)
        self.assertIsInstance(simulator, monte_carlo)

    def test_turn(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d')
        simulator = self.manager.find_simulator(2, *cards)
        self.assertIsInstance(simulator, simulation.BruteForceSimulator)

    def test_river(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d 5h')
        simulator = self.manager.find_simulator(2, *cards)
        self.assertIsInstance(simulator, simulation.BruteForceSimulator)

    def test_river_five_players(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d 5h')
        simulator = self.manager.find_simulator(5, *cards)
        self.assertIsInstance(simulator, monte_carlo)

    def test_turn_seven_players(self):
        cards = model.Card.parse_cards_line('As 6c Ad 8s Ac 4d')
        simulator = self.manager.find_simulator(7, *cards)
        self.assertIsInstance(simulator, monte_carlo)


class TestSimulationResult(unittest.TestCase):
    def test_beaten_by(self):
        beaten_by = [0, 0, 5824, 2736, 324, 849, 1478, 135, 6]
        result = simulation.SimulationResult(35000, 1600, 1100, None, beaten_by)
        dangerous_hands = result.sorted_beating_hands[:3]
        self.assertEqual(3, len(dangerous_hands))
        self.assertEqual(dangerous_hands[0][0], model.Hand.TWO_PAIR)
        self.assertEqual(dangerous_hands[0][1], 5824)
        self.assertEqual(dangerous_hands[2][0], model.Hand.FULL_HOUSE)
        self.assertEqual(dangerous_hands[2][1], 1478)
