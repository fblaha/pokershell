from functools import total_ordering

_SUITS = {'♣': ('c', 1),
          '♦': ('d', 2),
          '♥': ('h', 3),
          '♠': ('s', 4)}
_SUITS_CODE = {v[0]: k for k, v in _SUITS.items()}

_RANKS = '2 3 4 5 6 7 8 9 J Q K A'.split()
_RANKS_ORD = {rank: i for i, rank in enumerate(_RANKS)}


@total_ordering
class Card:
    def __init__(self, rank, suit):
        self._check_rank(rank)
        self._check_suite(suit)
        self._rank = rank
        self._suit = suit

    @staticmethod
    def _check_rank(rank):
        if rank not in _RANKS:
            raise ValueError('Invalid rank: {0}'.format(rank))

    @staticmethod
    def _check_suite(value):
        if value not in _SUITS:
            raise ValueError('Invalid suit: {0}'.format(value))

    @property
    def suit(self):
        return self._suit

    @property
    def rank(self):
        return self._rank

    def __key(self):
        return _RANKS_ORD[self._rank], _SUITS[self._suit][1]

    def __eq__(self, y):
        return isinstance(y, self.__class__) and self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    @staticmethod
    def parse(card_str):
        if len(card_str) != 2:
            raise ValueError('Invalid card: {0}'.format(card_str))
        rank = card_str[0].upper()
        suit = card_str[1].lower()
        if suit not in _SUITS_CODE:
            raise ValueError('Invalid suit: {0}'.format(suit))
        return Card(rank, _SUITS_CODE[suit])

    def __str__(self):
        return self._rank + self._suit
