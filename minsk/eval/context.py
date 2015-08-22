import collections
import functools


class EvalContext:
    def __init__(self, *cards):
        super().__init__()
        self._cards = cards
        self._by_rank = None
        self._by_suit = None

    @property
    def by_rank(self):
        if self._by_rank:
            return self._by_rank
        self._by_rank = collections.defaultdict(set)
        for card in self._cards:
            self._by_rank[card.rank].add(card)
        return self._by_rank

    @property
    def by_suit(self):
        if self._by_suit:
            return self._by_suit
        self._by_suit = collections.defaultdict(set)
        for card in self._cards:
            self._by_suit[card.suit].add(card)
        return self._by_suit

    @functools.lru_cache(maxsize=10)
    def get_ranks(self, count, check_better=True):
        ranks = []
        for rank, cards in self.by_rank.items():
            if check_better and len(cards) > count:
                raise ValueError('Better hand is there: {0}'.format(cards))
            elif len(cards) == count:
                ranks.append(rank)
        ranks.sort(reverse=True)
        return ranks
