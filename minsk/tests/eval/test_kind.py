import testtools

import minsk.eval.context as context
import minsk.model as model

from minsk.eval.kind import FourEvaluator, ThreeEvaluator, \
    OnePairEvaluator, HighCardEvaluator, FullHouseEvaluator

parse = model.Card.parse_combo


class TestFourEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FourEvaluator()

    def test_eval(self):
        combo = parse('Js Jc Jh 2c 3c')
        outs = self.evaluator.get_outs(*combo)
        self.assertEqual({model.Card.parse('Jd')}, outs)

    def test_find(self):
        combo = parse('Js Jc 2h Jh 2c 3c Jd')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual((model.Rank.JACK,), result)


class TestThreeEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = ThreeEvaluator()

    def test_find(self):
        combo = parse('2h 2c 2d 5h Jh Js Jc')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual((model.Rank.JACK,), result)


class TestOnePairEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = OnePairEvaluator()

    def test_find(self):
        combo = parse('2h 2c 5h Jh qs Jc')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual((model.Rank.JACK,), result)

    def test_find_better(self):
        combo = parse('2h 2c 2d 5h Jh qs Jc')
        self.assertRaises(ValueError, self.evaluator.find, context.EvalContext(*combo))


class TestHighCardEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = HighCardEvaluator()

    def test_find(self):
        combo = parse('2h  5h Jh qs')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual((model.Rank.QUEEN,), result)


class TestFullHousedEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FullHouseEvaluator()

    def test_find_32(self):
        combo = parse('2h 2c 2d 5h Jh Jc')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual((model.Rank.DEUCE, model.Rank.JACK), result)

    def test_find_33(self):
        combo = parse('2h 2c 2d 5h Jh Jc Jd')
        result = self.evaluator.find(context.EvalContext(*combo))
        self.assertEqual((model.Rank.JACK, model.Rank.DEUCE), result)
