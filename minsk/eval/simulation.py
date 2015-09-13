import functools
import multiprocessing
import abc
import os
import random

import minsk.config as config
import minsk.model as model
import minsk.eval.manager as manager


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


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
            process_fc = functools.partial(self._process, cards)
            pool = multiprocessing.Pool()
            combinations = model.Card.all_combinations(deck_cards, unknown_count)
            partial_results = pool.map(process_fc, combinations)
            return tuple(sum(x) for x in zip(*partial_results))
        else:
            return self.simulate_river(*cards)

    def _process(self, cards, generated):
        return self.simulate_river(*(cards + generated))

    @abc.abstractmethod
    def simulate_river(self, *cards):
        pass


class BruteForceSimulator(CombinatoricSimulator):
    priority = 0
    name = 'Brute Force'
    cards_num = {6, 7}
    players_num = {2}

    def simulate_river(self, *cards):
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


class MonteCarloSimulator(CombinatoricSimulator):
    name = 'Monte Carlo'
    cards_num = {5, 6, 7}
    players_num = set(range(2, 11))

    def __init__(self, player_num, sim_num):
        super().__init__()
        self._player_num = player_num
        self._sim_num = sim_num

    def simulate_river(self, *cards):
        common = cards[2:]
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        best_hand = self._manager.find_best_hand(*cards)
        win, tie, lose, cnt = 0, 0, 0, 0
        while cnt < self._sim_num:
            others_cards = random.sample(deck_cards, (self._player_num - 1) * 2)
            hands = chunks(others_cards, 2)
            for hand in hands:
                opponent_cards = tuple(hand) + common
                opponent_best = self._manager.find_best_hand(*opponent_cards)
                cnt += 1
                is_tie, is_lose = False, False
                if best_hand < opponent_best:
                    is_lose = True
                    break
                elif best_hand == opponent_best:
                    is_tie = True
            if is_lose:
                lose += 1
            elif is_tie:
                tie += 1
            else:
                win += 1
        return win, tie, lose

    @classmethod
    def from_config(cls):
        return cls(config.player_num, config.sim_cycles)


class PreFlopSimulator(AbstractSimulator):
    name = 'Pre-flop'
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
    simulators = (PreFlopSimulator, MonteCarloSimulator, BruteForceSimulator)

    def find_simulator(self, *cards):
        available = []
        for simulator in self.simulators:
            if config.player_num in simulator.players_num \
                    and len(cards) in simulator.cards_num:
                available.append(simulator)
        if available:
            best = sorted(available, key=lambda sim: sim.priority)[0]
            return best.from_config()
