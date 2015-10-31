import functools
import multiprocessing
import abc
import os
import random

import minsk.config as config
import minsk.model as model
import minsk.eval.manager as manager
import minsk.utils as utils


class SimulationResult(utils.CommonReprMixin):
    def __init__(self, win, tie, lose, beaten_by):
        self.win = win
        self.tie = tie
        self.lose = lose
        self.beaten_by = beaten_by

    @property
    def total(self):
        return self.win + self.tie + self.lose

    def get_dangerous_hands(self, n):
        if self.beaten_by:
            counts = [(hand, self.beaten_by[hand]) for hand in model.Hand]
            counts.sort(key=lambda x: x[1], reverse=True)
            return [cnt for cnt in counts[:n] if cnt[1]]


class AbstractSimulator(metaclass=abc.ABCMeta):
    priority = 100

    @abc.abstractmethod
    def simulate(self, *cards):
        pass

    @classmethod
    @abc.abstractclassmethod
    def from_config(cls):
        pass


class ParallelSimulatorMixin:
    @staticmethod
    def _simulate_parallel(sim_fc, data):
        partial_results = multiprocessing.Pool().map(sim_fc, data)
        win, tie, lose = 0, 0, 0
        beaten_by = [0] * len(model.Hand)
        for result in partial_results:
            win += result.win
            tie += result.tie
            lose += result.lose
            for i, cnt in enumerate(result.beaten_by):
                beaten_by[i] += cnt
        return SimulationResult(win, tie, lose, beaten_by)

    @classmethod
    def _simulate_cards_parallel(cls, sim_cycles, fc, cards):
        parallel_count = multiprocessing.cpu_count() * 2
        start_data = (cards,) * parallel_count
        cycles = sim_cycles // parallel_count
        fc = functools.partial(fc, cycles)
        return cls._simulate_parallel(fc, start_data)


class BruteForceSimulator(AbstractSimulator, ParallelSimulatorMixin):
    priority = 0
    name = 'Brute Force'
    cards_num = {6, 7}
    players_num = {2}

    def __init__(self):
        super().__init__()
        self._manager = manager.EvaluatorManager()

    def _process(self, parallel_exec_num, cards, generated):
        return self._simulate_river(parallel_exec_num, cards + generated)

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

    def _simulate_river(self, _, cards):
        common = cards[2:]
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        best_hand = self._manager.find_best_hand(cards)
        beaten_by = [0] * len(model.Hand)
        win, tie, lose = 0, 0, 0
        for opponent in model.Card.all_combinations(deck_cards, 2):
            opponent_cards = opponent + common
            opponent_best = self._manager.find_best_hand(opponent_cards,
                                                         min_hand=best_hand.hand)
            if not opponent_best or best_hand > opponent_best:
                win += 1
            elif best_hand < opponent_best:
                beaten_by[opponent_best.hand] += 1
                lose += 1
            elif best_hand == opponent_best:
                tie += 1

        return SimulationResult(win, tie, lose, beaten_by)

    @classmethod
    def from_config(cls):
        return cls()


class MonteCarloSimulator(AbstractSimulator, ParallelSimulatorMixin):
    name = 'Monte Carlo'
    cards_num = set(range(2, 8))
    players_num = set(range(2, 11))

    def __init__(self, player_num, sim_cycles):
        super().__init__()
        self._manager = manager.EvaluatorManager()
        self._player_num = player_num
        self._sim_cycles = sim_cycles
        self._avg_eval_count = self._get_avg_eval_count(player_num - 1)

    @staticmethod
    def _get_avg_eval_count(opponents_count):
        prob, sum = 1.0, 0.0
        for i in range(1, opponents_count):
            prob /= 2
            sum += i * prob
        sum += opponents_count * prob
        return sum

    def simulate(self, *cards):
        return self._simulate_cards_parallel(self._sim_cycles, self._sample, cards)

    def _sample(self, sim_cycles, cards):
        common = cards[2:]
        sampled_common_count = 5 - len(common)
        deck_cards = model.Deck(*cards).cards
        win, tie, lose = 0, 0, 0
        others_count = self._player_num - 1
        sampled_count = sampled_common_count + others_count * 2
        beaten_by = [0] * len(model.Hand)
        for _ in range(int(sim_cycles / (self._avg_eval_count + 1))):
            sampled_cards = tuple(random.sample(deck_cards, sampled_count))
            sampled_common = sampled_cards[:sampled_common_count]
            my_cards = cards + sampled_common
            my_hand = self._manager.find_best_hand(my_cards)
            others_cards = sampled_cards[sampled_common_count:]
            result, hand = self._eval_showdown(my_hand,
                                               common + sampled_common,
                                               others_cards)
            if result == -1:
                beaten_by[hand] += 1
                lose += 1
            elif result == 0:
                tie += 1
            else:
                win += 1
        return SimulationResult(win, tie, lose, beaten_by)

    def _eval_showdown(self, my_hand, common, others_cards):
        result = 1, my_hand.hand
        for hand in zip(others_cards[::2], others_cards[1::2]):
            opponent_cards = hand + common
            opponent_best = self._manager.find_best_hand(opponent_cards,
                                                         min_hand=my_hand.hand)
            if opponent_best:
                if my_hand < opponent_best:
                    return -1, opponent_best.hand
                    break
                elif my_hand == opponent_best:
                    result = 0, my_hand.hand
        return result

    @classmethod
    def from_config(cls):
        return cls(config.player_num, config.sim_cycles)


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
            code_dict[code] = SimulationResult(win, tie, lose, None)
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
    simulators = (LookUpSimulator,
                  BruteForceSimulator,
                  MonteCarloSimulator)

    def find_simulator(self, *cards):
        available = []
        for simulator in self.simulators:
            if config.player_num in simulator.players_num \
                    and len(cards) in simulator.cards_num:
                available.append(simulator)
        if available:
            best = sorted(available, key=lambda sim: sim.priority)[0]
            return best.from_config()
