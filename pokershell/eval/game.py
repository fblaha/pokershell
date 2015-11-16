import enum

import pokershell.utils as utils


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
        self._previous = None

    def is_successor(self, other):
        if self == other:
            return False
        my_cards = ''.join(map(repr, self._cards))
        other_cards = ''.join(map(repr, other._cards))
        return all((my_cards.startswith(other_cards),
                    other.pot is None or self.pot >= other.pot,
                    other.player_num is None or self.player_num <= other.player_num,))

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
    def pot_growth(self):
        if self.pot and self.previous and self.previous.pot:
            return self.pot / self.previous.pot

    @property
    def fold_num(self):
        if self.player_num and self.previous and self.previous.player_num:
            return self.previous.player_num - self.player_num

    @property
    def street(self):
        return Street(len(self._cards))

    @property
    def history(self):
        result, current = [], self
        while current is not None:
            result.append(current)
            current = current.previous
        return result

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, previous):
        if previous and not self.is_successor(previous):
            raise ValueError('State %s is not successor of %s' % (self, previous))
        self._previous = previous
