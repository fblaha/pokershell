import collections

import minsk.model as model
import minsk.eval as eval


class KindEvaluator(eval.AbstractEvaluator):
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
                suit = set(model.Suit) - {card.suit for card in cards}
                return {model.Card(rank, suit.pop())}

    def find(self, context):
        ranks = context.get_ranks(self._count)
        if ranks:
            return ranks[0],


class FourEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(model.Hand.FOUR_OF_KIND, 4)


class ThreeEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(model.Hand.THREE_OF_KIND, 3)


class OnePairEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(model.Hand.ONE_PAIR, 2)


class HighCardEvaluator(KindEvaluator):
    def __init__(self):
        super().__init__(model.Hand.HIGH_CARD, 1)


class FullHouseEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        ranks3 = context.get_ranks(3)
        if ranks3:
            ranks2 = []
            if len(ranks3) == 2:
                ranks2.append(ranks3[1])
            ranks2 += context.get_ranks(2, check_better=False)
            ranks2.sort(reverse=True)
            if ranks2:
                return ranks3[0], ranks2[0]
