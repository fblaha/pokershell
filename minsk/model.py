import enum
import functools
import random

import minsk.utils


class Suit(enum.Enum):
    CLUBS = '♣', 'c', 'clubs'
    DIAMONDS = '♦', 'd', 'diamonds'
    HEARTS = '♥', 'h', 'hearts'
    SPADES = '♠', 's', 'spades'

    def __repr__(self):
        return self.value[0]


class Rank(enum.Enum):
    DEUCE = '2', 2
    THREE = '3', 3
    FOUR = '4', 4
    FIVE = '5', 5
    SIX = '6', 6
    SEVEN = '7', 7
    EIGHT = '8', 8
    NINE = '9', 9
    TEN = 'T', 10
    JACK = 'J', 11
    QUEEN = 'Q', 12
    KING = 'K', 13
    ACE = 'A', 1

    def __repr__(self):
        return self.value[0]


_SUIT_ORD = {suit: i for i, suit in enumerate(Suit)}
_RANK_ORD = {rank: i for i, rank in enumerate(Rank)}


@functools.total_ordering
class Card(metaclass=minsk.utils.MementoMetaclass):
    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    @property
    def suit(self):
        return self._suit

    @property
    def rank(self):
        return self._rank

    def __key(self):
        return _RANK_ORD[self._rank], _SUIT_ORD[self._suit]

    def __eq__(self, y):
        return isinstance(y, self.__class__) and self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def __repr__(self):
        return repr(self._rank) + repr(self._suit)

    @staticmethod
    def parse(card_str):
        if len(card_str) != 2:
            raise ValueError('Invalid card: {0}'.format(card_str))
        rank_str = card_str[0].upper()
        suit_str = card_str[1].lower()
        if rank_str not in {r.value[0] for r in Rank}:
            raise ValueError('Invalid rank: {0}'.format(rank_str))
        if suit_str not in {s.value[1] for s in Suit}:
            raise ValueError('Invalid rank: {0}'.format(rank_str))
        rank = [rank for rank in Rank if rank.value[0] == rank_str][0]
        suit = [suit for suit in Suit if suit.value[1] == suit_str][0]
        return Card(rank, suit)

    @staticmethod
    def parse_combo(line):
        cards_str = line.split()
        return [Card.parse(card) for card in cards_str]


class Deck:
    def __init__(self):
        super().__init__()
        self._cards = [Card(rank, suit) for rank in Rank for suit in Suit]

    def shuffle(self):
        random.shuffle(self._cards)

    def __repr__(self):
        return repr(self._cards)

    def pop(self):
        if self._cards:
            return self._cards.pop()

    def __key(self):
        return self._cards

    def __eq__(self, y):
        return isinstance(y, self.__class__) and self.__key() == y.__key()
