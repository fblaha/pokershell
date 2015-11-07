import enum

import minsk.utils as utils


@enum.unique
class Street(enum.IntEnum):
    PRE_FLOP = 2
    FLOP = 5
    TURN = 6
    RIVER = 7


class GameState(utils.CommonEqualityMixin, utils.CommonReprMixin):
    def __init__(self, cards, player_num, pot):
        super().__init__()
        if player_num and not 2 <= player_num <= 10:
            raise ValueError('Illegal player number %d' % player_num)
        self._cards = cards
        self._player_num = player_num
        self._pot = pot

    def is_successor(self, other):
        if self == other:
            return False
        my_cards = ''.join(map(repr, self._cards))
        other_cards = ''.join(map(repr, other._cards))
        return all((my_cards.startswith(other_cards),
                    other.pot is None or self.pot >= other.pot,
                    self.player_num <= other.player_num,))

    @property
    def cards(self):
        return self._cards

    @property
    def player_num(self):
        return self._player_num

    @property
    def pot(self):
        return self._pot

    @property
    def street(self):
        return Street(len(self._cards))


class GameStack(utils.CommonReprMixin):
    def __init__(self):
        super().__init__()
        self._history = []

    def add_state(self, state):
        if self._history and not state.is_successor(self._history[-1]):
            raise ValueError('State %s is not successor of %s' % (state, self._history[-1]))
        self._history.append(state)

    @property
    def history(self):
        return self._history

    @property
    def current(self):
        if self._history:
            return self._history[-1]
