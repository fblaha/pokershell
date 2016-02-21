import pokershell.eval as eval
import pokershell.model as model


class KindEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        ranks = context.get_ranks(self.count)
        if ranks:
            def get_ranks():
                complement_count = 5 - self.count
                result = context.get_complement_ranks(complement_count, ranks[0])
                result.insert(0, ranks[0])
                return tuple(result)

            return get_ranks


class FourEvaluator(KindEvaluator):
    count = 4
    required_rank_counts = {count}


class ThreeEvaluator(KindEvaluator):
    count = 3
    required_rank_counts = {count}


class OnePairEvaluator(KindEvaluator):
    count = 2
    required_rank_counts = {count}


class HighCardEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        return lambda: tuple(context.get_complement_ranks(5))


class FullHouseEvaluator(eval.AbstractEvaluator):
    required_rank_counts = {3}

    def find(self, context):
        ranks3 = context.get_ranks(3)
        if ranks3:
            ranks2 = []
            if len(ranks3) == 2:
                ranks2.append(ranks3[1])
            ranks2 += context.get_ranks(2, check_better=False)
            ranks2.sort(reverse=True)
            if ranks2:
                return lambda: (ranks3[0], ranks2[0])


class TwoPairsEvaluator(eval.AbstractEvaluator):
    required_rank_counts = {2}

    def find(self, context):
        ranks2 = context.get_ranks(2)
        if len(ranks2) >= 2:
            def get_ranks():
                complement = context.get_complement_ranks(1, ranks2[0], ranks2[1])
                return ranks2[0], ranks2[1], complement[0]

            return get_ranks


class FlushEvaluator(eval.AbstractEvaluator):
    required_suit_count = 5

    def find(self, context):
        by_suit = context.suit_dict
        sorted_sets = sorted(by_suit.values(), key=len, reverse=True)
        if sorted_sets:
            biggest = sorted_sets[0]
            if len(biggest) >= 5:
                def get_ranks():
                    sorted_cards = sorted(biggest, key=lambda card: card.rank,
                                          reverse=True)[0:5]
                    return tuple(card.rank for card in sorted_cards)

                return get_ranks


class StraightEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        return self._find_straight(context.cards)

    @staticmethod
    def _find_straight(cards):
        ranks = {card.rank for card in cards}
        rank_nums = sorted(map(lambda rank: rank.value[1], ranks), reverse=True)
        if model.Rank.ACE in ranks:
            rank_nums.append(1)
        for rank_ord in rank_nums:
            lower = rank_ord - 4
            if all(r in rank_nums for r in range(lower, rank_ord + 1)):
                return lambda: (model.Rank.from_ord(rank_ord),)


class StraightFlushEvaluator(StraightEvaluator):
    required_suit_count = 5

    def find(self, context):
        for suit_set in context.suit_dict.values():
            if len(suit_set) >= 5:
                result = self._find_straight(suit_set)
                if result:
                    return result
