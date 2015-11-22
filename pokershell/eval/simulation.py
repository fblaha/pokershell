import abc
import contextlib
import functools
import multiprocessing
import os
import random
import time

import pokershell.config as config
import pokershell.eval.manager as manager
import pokershell.model as model
import pokershell.utils as utils


class SimulatorManager:
    simulators = []

    @classmethod
    def register_simulator(cls, sim_class):
        cls.simulators.append(sim_class)

    def find_simulator(self, player_num, *cards):
        assert isinstance(player_num, int)
        available = []
        for simulator in self.simulators:
            if player_num in simulator.players_num \
                    and len(cards) in simulator.cards_num:
                available.append(simulator)
        if available:
            best = sorted(available, key=lambda sim: sim.priority)[0]
            return best.from_config()


class SimulationResult(utils.CommonReprMixin):
    def __init__(self, win, tie, lose, winning_hands, beating_hands):
        self.win = win
        self.tie = tie
        self.lose = lose
        self._winning_hands = winning_hands
        self._beating_hands = beating_hands

    @property
    def total(self):
        return self.win + self.tie + self.lose

    @property
    def win_rate(self):
        return self.win / self.total

    @property
    def beating_hands(self):
        return self._beating_hands

    @property
    def winning_hands(self):
        return self._winning_hands

    @property
    def sorted_beating_hands(self):
        return self._get_frequent(self._beating_hands)

    @property
    def sorted_winning_hands(self):
        return self._get_frequent(self._winning_hands)

    @staticmethod
    def _get_frequent(lst):
        if lst:
            counts = [(hand, lst[hand]) for hand in model.Hand]
            counts.sort(key=lambda x: x[1], reverse=True)
            return [cnt for cnt in counts if cnt[1]]
        else:
            return []


class AbstractSimulator(metaclass=abc.ABCMeta):
    priority = 100

    @abc.abstractmethod
    def simulate(self, player_num, *cards):
        pass

    @classmethod
    def from_config(cls):
        return cls()


class ParallelSimulatorMixin:
    @classmethod
    def _simulate_parallel(cls, sim_fc, data):
        with contextlib.closing(multiprocessing.Pool()) as pool:
            partial_results = pool.map(sim_fc, data)
            win, tie, lose = 0, 0, 0
            beating, winning = [0] * len(model.Hand), [0] * len(model.Hand)
            for result in partial_results:
                win += result.win
                tie += result.tie
                lose += result.lose
                cls._add_list(result.beating_hands, beating)
                cls._add_list(result.winning_hands, winning)
            return SimulationResult(win, tie, lose, winning, beating)

    @staticmethod
    def _add_list(target_lst, add_lst):
        for i, cnt in enumerate(target_lst):
            add_lst[i] += cnt


class BruteForceSimulator(AbstractSimulator, ParallelSimulatorMixin):
    """Uses brute force to simulate all possible game outcomes.
    Simulator evaluates all permutations of unknown cards and gives accurate results.
    From performance reason is usable only for limited unknown cards number.
    Allows simulate game only with 2 players after turn.
    """
    priority = 0
    name = 'brute-force'
    cards_num = {6, 7}
    players_num = {2}

    def __init__(self):
        super().__init__()
        self._manager = manager.EvaluatorManager()

    def _process(self, cards, generated):
        return self._simulate_river(cards + generated)

    def simulate(self, player_num, *cards):
        assert isinstance(player_num, int)
        if player_num != 2:
            raise ValueError('Only 2 players are supported')
        unknown_count = 7 - len(cards)
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        if unknown_count:
            fc = functools.partial(self._process, cards)
            combinations = model.Card.all_combinations(deck_cards, unknown_count)
            return self._simulate_parallel(fc, combinations)
        else:
            return self._simulate_river(cards)

    def _simulate_river(self, cards):
        common = cards[2:]
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        best_hand = self._manager.find_best_hand(cards)
        beaten_by, win_by = [0] * len(model.Hand), [0] * len(model.Hand)
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
        win_by[best_hand.hand] = win
        return SimulationResult(win, tie, lose, win_by, beaten_by)


class MonteCarloSimulator(AbstractSimulator, ParallelSimulatorMixin):
    """Uses Monte Carlo method to calculate game outcome.
    Simulator randomly samples unknown cards in game.
    Results are inaccurate. Result accuracy depends on simulation duration."""
    name = 'monte-carlo'
    cards_num = set(range(2, 8))
    players_num = set(range(2, 11))
    sim_cycle = config.register_option(name='sim-cycle', value=1, type=int, short='-t',
                                       description='Duration of Monte Carlo '
                                                   'simulation in seconds')

    def __init__(self, sim_cycle=1):
        super().__init__()
        self._manager = manager.EvaluatorManager()
        if sim_cycle > 120:
            raise ValueError('Too long simulation %f seconds' % sim_cycle)
        self._sim_cycle = sim_cycle

    def simulate(self, player_num, *cards):
        assert isinstance(player_num, int)
        start_data = (cards,) * multiprocessing.cpu_count()
        fc = functools.partial(self._sample, player_num, self._sim_cycle)
        return self._simulate_parallel(fc, start_data)

    def _sample(self, player_num, sim_cycle, cards):
        start = time.time()
        common = cards[2:]
        sampled_common_count = 5 - len(common)
        deck_cards = model.Deck(*cards).cards
        win, tie, lose = 0, 0, 0
        others_count = player_num - 1
        sampled_count = sampled_common_count + others_count * 2
        win_by, beaten_by = [0] * len(model.Hand), [0] * len(model.Hand)
        while time.time() - start < sim_cycle:
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
                win_by[my_hand.hand] += 1
                win += 1
        return SimulationResult(win, tie, lose, win_by, beaten_by)

    def _eval_showdown(self, my_hand, common, others_cards):
        result = 1, my_hand.hand
        for hand in zip(others_cards[::2], others_cards[1::2]):
            opponent_cards = hand + common
            opponent_best = self._manager.find_best_hand(opponent_cards,
                                                         min_hand=my_hand.hand)
            if opponent_best:
                if my_hand < opponent_best:
                    return -1, opponent_best.hand
                elif my_hand == opponent_best:
                    result = 0, my_hand.hand
        return result

    @classmethod
    def from_config(cls):
        return cls(cls.sim_cycle.value)


class LookUpSimulator(AbstractSimulator):
    """Uses database of simulated games outcomes.
    Database contains simulation results only for pre-flop phase.
    Simulator is intended to evaluate strength of player's hand before the flop.
    """
    priority = 0
    name = 'look-up'
    cards_num = {2}
    players_num = set(range(2, 11))

    def __init__(self):
        super().__init__()
        self._sim_data = {}

    def _init_data(self, player_num):
        if player_num in self._sim_data:
            return
        code_dict = {}
        directory = os.path.dirname(__file__)
        data_file = os.path.join(directory, 'preflop', str(player_num) + '.txt')
        with open(data_file) as f:
            content = f.readlines()
        for line in content:
            line_split = line.split()
            code = line_split[1]
            win = float(line_split[2])
            tie = float(line_split[3])
            lose = 100 - win - tie
            code_dict[code] = SimulationResult(win, tie, lose, None, None)
        self._sim_data[player_num] = code_dict

    def simulate(self, player_num, c1, c2):
        assert isinstance(player_num, int)
        self._init_data(player_num)
        code = self._get_hole_code(c1, c2)
        return self._sim_data[player_num][code]

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


SimulatorManager.register_simulator(LookUpSimulator)
SimulatorManager.register_simulator(BruteForceSimulator)
SimulatorManager.register_simulator(MonteCarloSimulator)
