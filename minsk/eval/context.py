import collections


class EvalContext:
    def __init__(self, *cards):
        super().__init__()
        self.cards = cards
        self._hole_ranks = None
        self._best_high_cards = None
        self._init_ranks()
        self._init_suits()

    def _init_ranks(self):
        self.rank_dict = collections.defaultdict(list)
        for card in self.cards:
            self.rank_dict[card.rank].append(card)
        self.rank_counts = set(map(len, self.rank_dict.values()))
        self.rank_num = len(self.rank_dict)

    def _init_suits(self):
        self.suit_dict = collections.defaultdict(list)
        for card in self.cards:
            self.suit_dict[card.suit].append(card)
        self.max_suit_count = max(map(len, self.suit_dict.values()))

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
            hole_ranks = [card.rank for card in self.cards[0:2]]
            self._hole_ranks = tuple(sorted(hole_ranks, reverse=True))
        return self._hole_ranks

    @property
    def best_high_cards(self):
        if not self._best_high_cards:
            _best_high_cards = [rank for rank, cards in self.rank_dict.items()
                                if len(cards) == 1]
            self._best_high_cards = sorted(_best_high_cards, reverse=True)
        return self._best_high_cards
