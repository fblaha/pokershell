import enum
import functools
import itertools
import random

import pokershell.utils as utils

enable_unicode = False


@enum.unique
class Suit(enum.Enum):
    CLUBS = '♣', 'c', 'clubs'
    DIAMONDS = '♦', 'd', 'diamonds'
    HEARTS = '♥', 'h', 'hearts'
    SPADES = '♠', 's', 'spades'

    def __repr__(self):
        if enable_unicode:
            return self.value[0]
        else:
            return self.value[1]


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
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_KIND = 7
    STRAIGHT_FLUSH = 8


class Card(utils.CommonEqualityMixin, metaclass=utils.MementoMetaclass):
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
        return self._rank, self._suit

    def __hash__(self):
        return hash(self.__key())

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

    @classmethod
    def parse_cards_line(cls, cards_line):
        return cls.parse_cards(cards_line.split())

    @classmethod
    def parse_cards(cls, tokens):
        return tuple(cls.parse(card) for card in tokens)


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
