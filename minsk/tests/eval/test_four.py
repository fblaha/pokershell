import testtools

from minsk.eval.four import FourEvaluator
from minsk.model import Card


class TestFourEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FourEvaluator()

    def test_eval(self):
        combo = Card.parse_combo('Js Jc Jh 2c 3c')
        outs = self.evaluator.get_outs(*combo)
        self.assertEqual({Card.parse('Jd')}, outs)
