import functools
import multiprocessing
import abc
import random

import minsk.model as model
import minsk.eval.manager as manager


class AbstractSimulator(metaclass=abc.ABCMeta):
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


class BruteForceSimulator(AbstractSimulator):
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


class MonteCarloSimulator(AbstractSimulator):
    def __init__(self, player_num, sim_num):
        super().__init__()
        self._player_num = int(player_num)
        self._sim_num = int(sim_num)

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
                is_tie = False
                if best_hand < opponent_best:
                    lose += 1
                    continue
                elif best_hand == opponent_best:
                    is_tie = True
            if is_tie:
                tie += 1
            else:
                win += 1
        return win, tie, lose


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
