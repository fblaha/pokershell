import functools
import multiprocessing
import abc
import os
import random

import minsk.config as config
import minsk.model as model
import minsk.eval.manager as manager


class AbstractSimulator(metaclass=abc.ABCMeta):
    priority = 100

    @abc.abstractmethod
    def simulate(self, *cards):
        pass

    @classmethod
    @abc.abstractclassmethod
    def from_config(cls):
        pass


class CombinatoricSimulator(AbstractSimulator, metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self._manager = manager.EvaluatorManager()

    def simulate(self, *cards):
        unknown_count = 7 - len(cards)
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        if unknown_count:
            parallel_exec_num = len(deck_cards) ** unknown_count
            fc = functools.partial(self._process, parallel_exec_num, cards)
            combinations = model.Card.all_combinations(deck_cards, unknown_count)
            return self._simulate_parallel(fc, combinations)
        else:
            return self._simulate_river(0, cards)

    @staticmethod
    def _simulate_parallel(sim_fc, data):
        partial_results = multiprocessing.Pool().map(sim_fc, data)
        return tuple(sum(x) for x in zip(*partial_results))

    def _process(self, parallel_exec_num, cards, generated):
        return self._simulate_river(parallel_exec_num, cards + generated)

    @abc.abstractmethod
    def _simulate_river(self, generated_num, cards):
        pass

    def _eval_showdown(self, my_hand, common, others_cards):
        result = 1
        for hand in zip(others_cards[::2], others_cards[1::2]):
            opponent_cards = hand + common
            opponent_best = self._manager.find_best_hand(*opponent_cards)
            if my_hand < opponent_best:
                return -1
                break
            elif my_hand == opponent_best:
                result = 0
        return result


class BruteForceSimulator(CombinatoricSimulator):
    priority = 0
    name = 'Brute Force'
    cards_num = {6, 7}
    players_num = {2}

    def _simulate_river(self, _, cards):
        common = cards[2:]
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        best_hand = self._manager.find_best_hand(*cards)
        win, tie, lose = 0, 0, 0
        for opponent in model.Card.all_combinations(deck_cards, 2):
            opponent_cards = opponent + common
            opponent_best = self._manager.find_best_hand(*opponent_cards)
            if len(best_hand) != len(opponent_best):
                raise ValueError('Hands are not comparable: {0} {1}'.
                                 format(best_hand, opponent_best))
            if best_hand > opponent_best:
                win += 1
            elif best_hand < opponent_best:
                lose += 1
            elif best_hand == opponent_best:
                tie += 1
        return win, tie, lose

    @classmethod
    def from_config(cls):
        return cls()


class HybridMonteCarloSimulator(CombinatoricSimulator):
    name = 'Hybrid Monte Carlo'
    cards_num = {5, 6, 7}
    players_num = set(range(2, 11))

    def __init__(self, player_num, sim_cycles):
        super().__init__()
        self._player_num = player_num
        self._sim_cycles = sim_cycles

    def _simulate_river(self, parallel_exec_num, cards):
        if parallel_exec_num:
            cycles = self._sim_cycles // parallel_exec_num
            return self._sample_opponents(cycles, cards)
        else:
            return self._simulate_cards_parallel(self._sim_cycles,
                                                 self._sample_opponents, cards)

    @classmethod
    def _simulate_cards_parallel(cls, sim_cycles, fc, cards):
        parallel_count = multiprocessing.cpu_count() * 2
        start_data = (cards,) * parallel_count
        cycles = sim_cycles // parallel_count
        fc = functools.partial(fc, cycles)
        return cls._simulate_parallel(fc, start_data)

    def _sample_opponents(self, sim_cycles, cards):
        common = cards[2:]
        deck_cards = model.Deck(*cards).cards
        my_hand = self._manager.find_best_hand(*cards)
        win, tie, lose = 0, 0, 0
        others_count = self._player_num - 1
        sampled_count = others_count * 2
        for _ in range(sim_cycles // others_count):
            others_cards = random.sample(deck_cards, sampled_count)
            result = self._eval_showdown(my_hand, common, others_cards)
            if result == -1:
                lose += 1
            elif result == 0:
                tie += 1
            else:
                win += 1
        return win, tie, lose

    @classmethod
    def from_config(cls):
        return cls(config.player_num, config.sim_cycles)


class MonteCarloSimulator(HybridMonteCarloSimulator):
    name = 'Monte Carlo'
    cards_num = set(range(2, 8))
    players_num = set(range(2, 11))

    def __init__(self, player_num, sim_cycles):
        super().__init__(player_num, sim_cycles)

    def simulate(self, *cards):
        return self._simulate_cards_parallel(self._sim_cycles, self._sample, cards)

    def _sample(self, sim_cycles, cards):
        common = cards[2:]
        sampled_common_count = 5 - len(common)
        deck_cards = model.Deck(*cards).cards
        win, tie, lose = 0, 0, 0
        others_count = self._player_num - 1
        sampled_count = sampled_common_count + others_count * 2
        for _ in range(sim_cycles // others_count):
            sampled_cards = tuple(random.sample(deck_cards, sampled_count))
            sampled_common = sampled_cards[:sampled_common_count]
            my_cards = cards + sampled_common
            my_hand = self._manager.find_best_hand(*my_cards)
            others_cards = sampled_cards[sampled_common_count:]
            result = self._eval_showdown(my_hand, common + sampled_common, others_cards)
            if result == -1:
                lose += 1
            elif result == 0:
                tie += 1
            else:
                win += 1
        return win, tie, lose


class LookUpSimulator(AbstractSimulator):
    priority = 0
    name = 'Look Up'
    cards_num = {2}
    players_num = set(range(2, 11))

    def __init__(self, player_num):
        super().__init__()
        self._player_num = player_num
        self._sim_data = {}

    def _init_data(self, player_num):
        if player_num in self._sim_data:
            return
        code_dict = {}
        dir = os.path.dirname(__file__)
        data_file = os.path.join(dir, 'preflop', str(self._player_num) + '.txt')
        with open(data_file) as f:
            content = f.readlines()
        for line in content:
            line_split = line.split()
            code = line_split[1]
            win = float(line_split[2])
            tie = float(line_split[3])
            lose = 100 - win - tie
            code_dict[code] = (win, tie, lose)
        self._sim_data[player_num] = code_dict

    def simulate(self, c1, c2):
        self._init_data(self._player_num)
        code = self._get_hole_code(c1, c2)
        return self._sim_data[self._player_num][code]

    def _get_hole_code(self, c1, c2):
        ranks = sorted([c1.rank, c2.rank])
        if c1.rank == c2.rank:
            return self._get_code(ranks)
        else:
            if c1.suit == c2.suit:
                return self._get_code(ranks) + 's'
            else:
                return self._get_code(ranks)

    @staticmethod
    def _get_code(ranks):
        return ranks[0].value[0] + ranks[1].value[0]

    @classmethod
    def from_config(cls):
        return cls(config.player_num)


class SimulatorManager:
    simulators = (LookUpSimulator, HybridMonteCarloSimulator, BruteForceSimulator)

    def find_simulator(self, *cards):
        available = []
        for simulator in self.simulators:
            if config.player_num in simulator.players_num \
                    and len(cards) in simulator.cards_num:
                available.append(simulator)
        if available:
            best = sorted(available, key=lambda sim: sim.priority)[0]
            return best.from_config()
