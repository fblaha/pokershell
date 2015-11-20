import functools

import pokershell.eval.context as context
import pokershell.eval.evaluators as evaluators
import pokershell.model as model


@functools.total_ordering
class EvalResult:
    def __init__(self, hand, ranks_lazy):
        super().__init__()
        self._complement_ranks = None
        self.hand = hand
        self._ranks_lazy = ranks_lazy

    def __eq__(self, other):
        return self.hand == other.hand and self.complement_ranks == other.complement_ranks

    def __lt__(self, other):
        if self.hand == other.hand:
            return self.complement_ranks < other.complement_ranks
        else:
            return self.hand < other.hand

    @property
    def complement_ranks(self):
        if not self._complement_ranks:
            self._complement_ranks = self._ranks_lazy()
        return self._complement_ranks


class EvaluatorManager:
    evaluators = [None] * len(model.Hand)

    @classmethod
    def register_evaluator(cls, hand, evaluator):
        assert cls.evaluators[hand] is None
        cls.evaluators[hand] = evaluator

    def find_best_hand(self, cards, min_hand=None):
        ctx = context.EvalContext(*cards)
        for hand in reversed(model.Hand):
            evaluator = self.evaluators[hand]
            if evaluator.required_rank_counts <= ctx.rank_counts \
                    and ctx.max_suit_count >= evaluator.required_suit_count:
                result = evaluator.find(ctx)
                if result:
                    return EvalResult(hand, result)
            if min_hand and hand == min_hand:
                return


register = EvaluatorManager.register_evaluator
register(model.Hand.STRAIGHT_FLUSH, evaluators.StraightFlushEvaluator())
register(model.Hand.FOUR_OF_KIND, evaluators.FourEvaluator())
register(model.Hand.FULL_HOUSE, evaluators.FullHouseEvaluator())
register(model.Hand.FLUSH, evaluators.FlushEvaluator())
register(model.Hand.STRAIGHT, evaluators.StraightEvaluator())
register(model.Hand.THREE_OF_KIND, evaluators.ThreeEvaluator())
register(model.Hand.TWO_PAIR, evaluators.TwoPairsEvaluator())
register(model.Hand.ONE_PAIR, evaluators.OnePairEvaluator())
register(model.Hand.HIGH_CARD, evaluators.HighCardEvaluator())
