import collections


class EvalContext:
    def __init__(self, *cards):
        super().__init__()
        self.cards = cards
        self._sorted_ranks = None
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
    def sorted_ranks(self):
        if not self._sorted_ranks:
            self._sorted_ranks = sorted(
                map(lambda card: card.rank, self.cards),
                reverse=True)
        return self._sorted_ranks

    def get_complement_ranks(self, count, *excluded_ranks):
        result = []
        for rank in self.sorted_ranks:
            if rank not in excluded_ranks:
                result.append(rank)
                if len(result) == count:
                    return result
