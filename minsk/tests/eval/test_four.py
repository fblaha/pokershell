import testtools

from minsk.eval.four import FourEvaluator
import minsk.model


class TestFourEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FourEvaluator()

    def test_eval(self):
        combo = minsk.model.Card.parse_combo('Js Jc Jh 2c 3c')
        outs = self.evaluator.get_outs(*combo)
        self.assertEqual({minsk.model.Card.parse('Jd')}, outs)

    def test_find(self):
        combo = minsk.model.Card.parse_combo('Js Jc 2h Jh 2c 3c Jd')
        result = self.evaluator.find(*combo)
        self.assertEqual((minsk.model.Hand.FOUR_OF_KIND, minsk.model.Rank.JACK), result)
