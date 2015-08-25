import enum
import functools
import random
import itertools

import minsk.utils


@enum.unique
class Suit(enum.Enum):
    CLUBS = '♣', 'c', 'clubs'
    DIAMONDS = '♦', 'd', 'diamonds'
    HEARTS = '♥', 'h', 'hearts'
    SPADES = '♠', 's', 'spades'

    def __repr__(self):
        return self.value[0]


@functools.total_ordering
@enum.unique
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
    ACE = 'A', 14

    @staticmethod
    def from_ord(num):
        for rank in Rank:
            if rank.value[1] == num:
                return rank

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value[1] < other.value[1]
        return NotImplemented

    def __repr__(self):
        return self.value[0]


@enum.unique
class Hand(enum.IntEnum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9


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
    def all_cards():
        return (Card(rank, suit) for rank in Rank for suit in Suit)

    @staticmethod
    def all_combinations(cards, r):
        return itertools.combinations(cards, r)

    @staticmethod
    def parse(card_str):
        if len(card_str) != 2:
            raise ValueError('Invalid card: {0}'.format(card_str))
        rank_str = card_str[0].upper()
        suit_str = card_str[1].lower()
        if rank_str not in {r.value[0] for r in Rank}:
            raise ValueError('Invalid rank: {0}'.format(rank_str))
        if suit_str not in {s.value[1] for s in Suit}:
            raise ValueError('Invalid suit: {0}'.format(suit_str))
        rank = [rank for rank in Rank if rank.value[0] == rank_str][0]
        suit = [suit for suit in Suit if suit.value[1] == suit_str][0]
        return Card(rank, suit)


class Deck:
    def __init__(self, *excluded_cards):
        super().__init__()
        excluded_set = set(excluded_cards)
        self._cards = []
        for card in Card.all_cards():
            if card not in excluded_set:
                self._cards.append(card)

    @property
    def cards(self):
        return tuple(self._cards)

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
