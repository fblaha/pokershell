import collections

import minsk.eval.context as context
import minsk.eval.evaluators as evaluators
import minsk.model as model


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

    def find_best_hand(self, *cards):
        ctx = context.EvalContext(*cards)
        for hand, evaluator in self._EVALUATORS.items():
            if evaluator.required_rank_counts < ctx.rank_counts \
                    and ctx.max_suit_count >= evaluator.required_suit_count:
                result = evaluator.find(ctx)
                if result:
                    return hand, result
