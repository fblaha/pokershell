import unittest

import pokershell.eval.evaluators as evaluators
import pokershell.model as model
import pokershell.tests.eval.common as common


class TestFourEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.FourEvaluator()

    def test_find(self):
        result = self.evaluator.find(self.create_context('Js Jc 2h Jh 2c 3c Jd'))
        self.assertEqual((model.Rank.JACK, model.Rank.THREE), result())

    def test_find_with_pair(self):
        result = self.evaluator.find(self.create_context('Js Jc 4c Jh 4s 3c Jd'))
        self.assertEqual((model.Rank.JACK, model.Rank.FOUR), result())


class TestThreeEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.ThreeEvaluator()

    def test_find(self):
        result = self.evaluator.find(self.create_context('2h 2c 2d 5h Jh Js Jc'))
        self.assertEqual((model.Rank.JACK, model.Rank.FIVE, model.Rank.DEUCE), result())


class TestOnePairEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.OnePairEvaluator()

    def test_find(self):
        result = self.evaluator.find(self.create_context('2h 8c 5h Jh qs Jc'))
        self.assertEqual((model.Rank.JACK, model.Rank.QUEEN,
                          model.Rank.EIGHT, model.Rank.FIVE), result())

    def test_find_better(self):
        context = self.create_context('2h 2c 2d 5h Jh qs Jc')
        self.assertRaises(ValueError, self.evaluator.find, context)


class TestHighCardEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.HighCardEvaluator()

    def test_find(self):
        result = self.evaluator.find(self.create_context('2h  5h Jh qs 7c'))
        self.assertEqual((model.Rank.QUEEN, model.Rank.JACK,
                          model.Rank.SEVEN, model.Rank.FIVE, model.Rank.DEUCE), result())


class TestFullHouseEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.FullHouseEvaluator()

    def test_find_32(self):
        result = self.evaluator.find(self.create_context('2h 2c 2d 5h Jh Jc'))
        self.assertEqual((model.Rank.DEUCE, model.Rank.JACK), result())

    def test_find_33(self):
        result = self.evaluator.find(self.create_context('2h 2c 2d 5h Jh Jc Jd'))
        self.assertEqual((model.Rank.JACK, model.Rank.DEUCE), result())


class TestTwoPairsEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.TwoPairsEvaluator()

    def test_find(self):
        result = self.evaluator.find(self.create_context('2h 2c 5h Jh Jc'))
        self.assertEqual((model.Rank.JACK, model.Rank.DEUCE, model.Rank.FIVE), result())


class TestFlushEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.FlushEvaluator()

    def test_find6(self):
        result = self.evaluator.find(self.create_context('Js Jc 5c Jh 2c 3c 4d qc'))
        self.assertEqual((model.Rank.QUEEN, model.Rank.JACK, model.Rank.FIVE),
                         result()[0:3])

    def test_find5(self):
        result = self.evaluator.find(self.create_context('Js 9c 5c Jh 2c 3c tc'))
        self.assertEqual((model.Rank.TEN, model.Rank.NINE, model.Rank.FIVE),
                         result()[0:3])

    def test_find_none(self):
        result = self.evaluator.find(self.create_context('Js 9s 5c Jh 2c 3h tc'))
        self.assertIsNone(result)


class TestStraightEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.StraightEvaluator()

    def test_find_best(self):
        result = self.evaluator.find(self.create_context('Js qc tc 9h 8c 7c Jc qh'))
        self.assertEqual((model.Rank.QUEEN,), result())

    def test_find(self):
        result = self.evaluator.find(self.create_context('3s 5c 4c 6h 6d 7c Jc qc'))
        self.assertEqual((model.Rank.SEVEN,), result())

    def test_find_ace_down(self):
        result = self.evaluator.find(self.create_context('3s 5c 4c 2h Ah 7c Jc qc'))
        self.assertEqual((model.Rank.FIVE,), result())

    def test_find_ace_up(self):
        result = self.evaluator.find(self.create_context('Js Kc Tc Jh 2c Ah Jc qc'))
        self.assertEqual((model.Rank.ACE,), result())


class TestStraightFlushEvaluator(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.evaluator = evaluators.StraightFlushEvaluator()

    def test_find(self):
        result = self.evaluator.find(self.create_context('Jh qh th 9h 8h 7h Jc qc'))
        self.assertEqual((model.Rank.QUEEN,), result())

    def test_find_ace_down(self):
        result = self.evaluator.find(self.create_context('3h 5h 4h 2h Ah 7c Jc qc'))
        self.assertEqual((model.Rank.FIVE,), result())

    def test_find_ace_up(self):
        result = self.evaluator.find(self.create_context('Js Kc Tc Jh 2c Ac Jc qc'))
        self.assertEqual((model.Rank.ACE,), result())
