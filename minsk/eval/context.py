import collections


class EvalContext:
    def __init__(self, *cards):
        super().__init__()
        self._cards = cards
        self._rank_dict = None
        self._suit_dict = None
        self._hole_ranks = None

    @property
    def cards(self):
        return self._cards

    @property
    def rank_dict(self):
        if self._rank_dict:
            return self._rank_dict
        self._rank_dict = collections.defaultdict(list)
        for card in self._cards:
            self._rank_dict[card.rank].append(card)
        return self._rank_dict

    @property
    def suit_dict(self):
        if self._suit_dict:
            return self._suit_dict
        self._suit_dict = collections.defaultdict(list)
        for card in self._cards:
            self._suit_dict[card.suit].append(card)
        return self._suit_dict

    def get_ranks(self, count, check_better=True):
        ranks = []
        for rank, cards in self.rank_dict.items():
            if check_better and len(cards) > count:
                raise ValueError('Better hand is there: {0}'.format(cards))
            elif len(cards) == count:
                ranks.append(rank)
        ranks.sort(reverse=True)
        return ranks

    @property
    def hole_ranks(self):
        if not self._hole_ranks:
            hole_ranks = [card.rank for card in self._cards[0:2]]
            self._hole_ranks = tuple(sorted(hole_ranks, reverse=True))
        return self._hole_ranks
