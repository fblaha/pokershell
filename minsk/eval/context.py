import collections
import functools


class EvalContext:
    def __init__(self, *cards):
        super().__init__()
        self._cards = cards
        self._rank_dict = None
        self._suit_dict = None

    @property
    def cards(self):
        return self._cards

    @property
    def rank_dict(self):
        if self._rank_dict:
            return self._rank_dict
        self._rank_dict = collections.defaultdict(set)
        for card in self._cards:
            self._rank_dict[card.rank].add(card)
        return self._rank_dict

    @property
    def suit_dict(self):
        if self._suit_dict:
            return self._suit_dict
        self._suit_dict = collections.defaultdict(set)
        for card in self._cards:
            self._suit_dict[card.suit].add(card)
        return self._suit_dict

    @functools.lru_cache()
    def get_ranks(self, count, check_better=True):
        ranks = []
        for rank, cards in self.rank_dict.items():
            if check_better and len(cards) > count:
                raise ValueError('Better hand is there: {0}'.format(cards))
            elif len(cards) == count:
                ranks.append(rank)
        ranks.sort(reverse=True)
        return ranks
