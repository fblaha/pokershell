import minsk.model as model
import minsk.eval as eval


class KindEvaluator(eval.AbstractEvaluator):
    def __init__(self, hand, count):
        super().__init__()
        self._hand = hand
        self._count = count

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


class TwoPairsEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        ranks2 = context.get_ranks(2)
        if len(ranks2) >= 2:
            ranks1 = context.get_ranks(1, check_better=False)
            return ranks2[0], ranks2[1], ranks1[0]


import minsk.eval as eval


class FlushEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        by_suit = context.suit_dict
        sorted_sets = sorted(by_suit.values(), key=len, reverse=True)
        if sorted_sets:
            biggest = sorted_sets[0]
            if len(biggest) >= 5:
                card_rank = lambda card: card.rank
                sorted_cards = sorted(biggest, key=card_rank, reverse=True)[0:5]
                return tuple(card.rank for card in sorted_cards)


class StraightEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        return self._find_straight(context.cards)

    @staticmethod
    def _find_straight(cards):
        ranks = {card.rank for card in cards}
        rank_nums = {rank.value[1] for rank in ranks}
        if model.Rank.ACE in ranks:
            rank_nums.add(1)
        upper_ranks = []
        for rank_ord in rank_nums:
            upper = rank_ord + 5
            if all(r in rank_nums for r in range(rank_ord, upper)):
                upper_ranks.append(model.Rank.from_ord(upper - 1))
        if upper_ranks:
            upper_ranks.sort(reverse=True)
            return tuple(upper_ranks[0:1])


class StraightFlushEvaluator(StraightEvaluator):
    def find(self, context):
        collected_ranks = []
        for suit_set in context.suit_dict.values():
            if len(suit_set) >= 5:
                result = self._find_straight(suit_set)
                if result:
                    collected_ranks += result
        if collected_ranks:
            collected_ranks.sort(reverse=True)
            return collected_ranks[0:1]
