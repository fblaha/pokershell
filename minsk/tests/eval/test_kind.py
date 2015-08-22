import testtools

import minsk.model as model
from minsk.eval.kind import FourEvaluator, ThreeEvaluator, \
    OnePairEvaluator, HighCardEvaluator, FullHouseEvaluator, TwoPairsEvaluator
from minsk.tests.eval import create_context


class TestFourEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FourEvaluator()

    def test_eval(self):
        combo = model.Card.parse_combo('Js Jc Jh 2c 3c')
        outs = self.evaluator.get_outs(*combo)
        self.assertEqual({model.Card.parse('Jd')}, outs)

    def test_find(self):
        result = self.evaluator.find(create_context('Js Jc 2h Jh 2c 3c Jd'))
        self.assertEqual((model.Rank.JACK,), result)


class TestThreeEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = ThreeEvaluator()

    def test_find(self):
        result = self.evaluator.find(create_context('2h 2c 2d 5h Jh Js Jc'))
        self.assertEqual((model.Rank.JACK,), result)


class TestOnePairEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = OnePairEvaluator()

    def test_find(self):
        result = self.evaluator.find(create_context('2h 2c 5h Jh qs Jc'))
        self.assertEqual((model.Rank.JACK,), result)

    def test_find_better(self):
        context = create_context('2h 2c 2d 5h Jh qs Jc')
        self.assertRaises(ValueError, self.evaluator.find, context)


class TestHighCardEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = HighCardEvaluator()

    def test_find(self):
        result = self.evaluator.find(create_context('2h  5h Jh qs'))
        self.assertEqual((model.Rank.QUEEN,), result)


class TestFullHouseEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FullHouseEvaluator()

    def test_find_32(self):
        result = self.evaluator.find(create_context('2h 2c 2d 5h Jh Jc'))
        self.assertEqual((model.Rank.DEUCE, model.Rank.JACK), result)

    def test_find_33(self):
        result = self.evaluator.find(create_context('2h 2c 2d 5h Jh Jc Jd'))
        self.assertEqual((model.Rank.JACK, model.Rank.DEUCE), result)


class TestTwoPairsEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = TwoPairsEvaluator()

    def test_find(self):
        result = self.evaluator.find(create_context('2h 2c 5h Jh Jc'))
        self.assertEqual((model.Rank.JACK, model.Rank.DEUCE, model.Rank.FIVE), result)
