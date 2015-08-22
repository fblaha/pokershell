import testtools

from minsk.eval.flush import FlushEvaluator
import minsk.eval.context as context
import minsk.model as model

parse = model.Card.parse_combo


class TestFlushEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FlushEvaluator()

    def test_find6(self):
        combo = parse('Js Jc 5c Jh 2c 3c Jc qc')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual([model.Rank.QUEEN, model.Rank.JACK, model.Rank.FIVE],
                         result[0:3])

    def test_find5(self):
        combo = parse('Js 9c 5c Jh 2c 3c tc')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual([model.Rank.TEN, model.Rank.NINE, model.Rank.FIVE], result[0:3])

    def test_find_none(self):
        combo = parse('Js 9s 5c Jh 2c 3h tc')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertIsNone(result)
