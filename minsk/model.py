from enum import Enum
from functools import total_ordering


class Suit(Enum):
    CLUBS = '♣', 'c', 'clubs'
    DIAMONDS = '♦', 'd', 'diamonds'
    HEARTS = '♥', 'h', 'hearts'
    SPADES = '♠', 's', 'spades'


class Rank(Enum):
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


_SUIT_ORD = {suit: i for i, suit in enumerate(Suit)}
_RANK_ORD = {rank: i for i, rank in enumerate(Rank)}


@total_ordering
class Card:
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

    @staticmethod
    def parse(card_str):
        if len(card_str) != 2:
            raise ValueError('Invalid card: {0}'.format(card_str))
        rank_str = card_str[0].upper()
        suit_str = card_str[1].lower()
        rank = [rank for rank in Rank if rank.value[0] == rank_str][0]
        suit = [suit for suit in Suit if suit.value[1] == suit_str][0]

        return Card(rank, suit)

    def __str__(self):
        return self._rank.value[0] + self._suit.value[0]
