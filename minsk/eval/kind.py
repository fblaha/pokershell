import collections

import minsk.model


def get_cards_by_rank(args):
    by_rank = collections.defaultdict(set)
    for card in args:
        by_rank[card.rank].add(card)
    return by_rank


def get_ranks(by_rank, count, check_better=True):
    ranks = []
    for rank, cards in by_rank.items():
        if check_better and len(cards) > count:
            raise ValueError('Better hand is there: {0}'.format(cards))
        elif len(cards) == count:
            ranks.append(rank)
    ranks = sorted(ranks, reverse=True)
    return ranks


class KindEvaluator:
    def __init__(self, hand, count):
        super().__init__()
        self._hand = hand
        self._count = count

    def get_outs(self, *args):
        by_rank = collections.defaultdict(list)
        for card in args:
            by_rank[card.rank].append(card)
        for rank, cards in by_rank.items():
            if len(cards) == 3:
                suit = set(minsk.model.Suit) - {card.suit for card in cards}
                return {minsk.model.Card(rank, suit.pop())}

    def find(self, *args):
        by_rank = get_cards_by_rank(args)
        ranks = get_ranks(by_rank, self._count)
        if ranks:
            return ranks[0],


class FourEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(minsk.model.Hand.FOUR_OF_KIND, 4)


class ThreeEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(minsk.model.Hand.THREE_OF_KIND, 3)


class OnePairEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(minsk.model.Hand.ONE_PAIR, 2)


class HighCardEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(minsk.model.Hand.HIGH_CARD, 1)


class FullHouseEvaluator:
    def find(self, *args):
        by_rank = get_cards_by_rank(args)
        ranks3 = get_ranks(by_rank, 3)
        if ranks3:
            ranks2 = get_ranks(by_rank, 2, check_better=False)
            if ranks2:
                return ranks3[0], ranks2[0]
