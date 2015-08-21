import testtools

from minsk.eval.kind import FourEvaluator, ThreeEvaluator, \
    OnePairEvaluator, HighCardEvaluator, FullHouseEvaluator
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
        self.assertEqual((minsk.model.Rank.JACK,), result)


class TestThreeEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = ThreeEvaluator()

    def test_find(self):
        combo = minsk.model.Card.parse_combo('2h 2c 2d 5h Jh Js Jc')
        result = self.evaluator.find(*combo)
        self.assertEqual((minsk.model.Rank.JACK,), result)


class TestOnePairEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = OnePairEvaluator()

    def test_find(self):
        combo = minsk.model.Card.parse_combo('2h 2c 5h Jh qs Jc')
        result = self.evaluator.find(*combo)
        self.assertEqual((minsk.model.Rank.JACK,), result)

    def test_find_better(self):
        combo = minsk.model.Card.parse_combo('2h 2c 2d 5h Jh qs Jc')
        self.assertRaises(ValueError, self.evaluator.find, *combo)


class TestHighCardEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = HighCardEvaluator()

    def test_find(self):
        combo = minsk.model.Card.parse_combo('2h  5h Jh qs')
        result = self.evaluator.find(*combo)
        self.assertEqual((minsk.model.Rank.QUEEN,), result)


class TestFullHousedEvaluator(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.evaluator = FullHouseEvaluator()

    def test_find(self):
        combo = minsk.model.Card.parse_combo('2h 2c 2d 5h Jh Jc')
        result = self.evaluator.find(*combo)
        self.assertEqual((minsk.model.Rank.DEUCE, minsk.model.Rank.JACK), result)
