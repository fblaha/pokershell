import collections

import minsk.model


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
        h1, h2 = args[0:2]
        by_rank = collections.defaultdict(set)
        for card in args:
            by_rank[card.rank].add(card)
        for rank, cards in by_rank.items():
            if len(cards) == self._count and {h1, h2} & cards:
                return self._hand, rank


class FourEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(minsk.model.Hand.FOUR_OF_KIND, 4)


class ThreeEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(minsk.model.Hand.THREE_OF_KIND, 3)
