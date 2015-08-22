import testtools

import minsk.eval.flush as flush
import minsk.model as model
from minsk.tests.eval import create_context


class TestFlushEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = flush.FlushEvaluator()

    def test_find6(self):
        result = self.evaluator.find(create_context('Js Jc 5c Jh 2c 3c Jc qc'))
        self.assertEqual([model.Rank.QUEEN, model.Rank.JACK, model.Rank.FIVE],
                         result[0:3])

    def test_find5(self):
        result = self.evaluator.find(create_context('Js 9c 5c Jh 2c 3c tc'))
        self.assertEqual([model.Rank.TEN, model.Rank.NINE, model.Rank.FIVE], result[0:3])

    def test_find_none(self):
        result = self.evaluator.find(create_context('Js 9s 5c Jh 2c 3h tc'))
        self.assertIsNone(result)
