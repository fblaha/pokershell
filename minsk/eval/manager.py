import collections
import functools

import minsk.eval.context as context
import minsk.eval.evaluators as evaluators
import minsk.model as model


@functools.total_ordering
class EvalResult:
    def __init__(self, hand, ranks_lazy):
        super().__init__()
        self._complement_ranks = None
        self.hand = hand
        self._ranks_lazy = ranks_lazy

    def __eq__(self, other):
        return self.hand == other.hand \
               and self.complement_ranks == other.complement_ranks

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
    _EVALUATORS = collections.OrderedDict([
        (model.Hand.STRAIGHT_FLUSH, evaluators.StraightFlushEvaluator()),
        (model.Hand.FOUR_OF_KIND, evaluators.FourEvaluator()),
        (model.Hand.FULL_HOUSE, evaluators.FullHouseEvaluator()),
        (model.Hand.FLUSH, evaluators.FlushEvaluator()),
        (model.Hand.STRAIGHT, evaluators.StraightEvaluator()),
        (model.Hand.THREE_OF_KIND, evaluators.ThreeEvaluator()),
        (model.Hand.TWO_PAIR, evaluators.TwoPairsEvaluator()),
        (model.Hand.ONE_PAIR, evaluators.OnePairEvaluator()),
        (model.Hand.HIGH_CARD, evaluators.HighCardEvaluator()),
    ])

    def find_best_hand(self, cards, min_hand=None):
        ctx = context.EvalContext(*cards)
        for hand, evaluator in self._EVALUATORS.items():
            if evaluator.required_rank_counts < ctx.rank_counts \
                    and ctx.max_suit_count >= evaluator.required_suit_count:
                result = evaluator.find(ctx)
                if result:
                    return EvalResult(hand, result)
            if min_hand and hand == min_hand:
                return
