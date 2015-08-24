import itertools

import minsk.model as model
import minsk.eval.manager as manager


class BruteForceSimulator:
    def __init__(self):
        super().__init__()
        self._manager = manager.EvaluatorManager()

    def simulate(self, *cards):
        common = cards[2:]
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        best_hand = self._manager.find_best_hand(*cards)
        win, tie, lose = 0, 0, 0
        for opponent in itertools.combinations(deck_cards, 2):
            opponent_cards = opponent + common
            opponent_best = self._manager.find_best_hand(*opponent_cards)
            if len(best_hand) != len(opponent_best):
                raise ValueError('Hands are not comarable: {0} {1}'.
                                 format(best_hand, opponent_best))
            if best_hand > opponent_best:
                win += 1
            elif best_hand < opponent_best:
                lose += 1
            elif best_hand == opponent_best:
                tie += 1
        return win, tie, lose
