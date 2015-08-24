import itertools

import minsk.model as model
import minsk.eval.manager as manager


class BruteForceSimulator:
    def __init__(self):
        super().__init__()
        self._manager = manager.EvaluatorManager()

    def simulate(self, *cards):
        hole = cards[0:2]
        common = cards[2:]
        deck = model.Deck(*cards)
        deck_cards = deck.cards
        best_hand = self._manager.find_best_hand(*cards)
        me_win = 0
        opponent_win = 0

        for opponent in itertools.combinations(deck_cards, 2):
            print('me {0} opponent {1} common {2}'.format(hole, opponent, common))
            opponent_cards = opponent + common
            opponent_best = self._manager.find_best_hand(*opponent_cards)
            print('RESULT: me {0} opponent {1}'.format(best_hand, opponent_best))
            if len(best_hand) != len(opponent_best):
                raise ValueError('Hands are not comarable: {0} {1}'.format(best_hand, opponent_best))
            if best_hand > opponent_best:
                me_win += 1
            elif best_hand < opponent_best:
                opponent_win += 1
        print('RESULT: me {0} opponent {1}'.format(me_win, opponent_win))
