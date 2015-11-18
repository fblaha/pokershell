import unittest

import pokershell.eval.manager as manager
import pokershell.model as model
import pokershell.tests.eval.common as common


class TestEvalResult(unittest.TestCase):
    def test_cmp_hand(self):
        flush = manager.EvalResult(model.Hand.FLUSH, lambda: (model.Rank.ACE,))
        high_card = manager.EvalResult(model.Hand.HIGH_CARD, lambda: (model.Rank.ACE,))
        self.assertTrue(flush > high_card)
        self.assertFalse(flush < high_card)

    def test_cmp_ranks(self):
        high1 = manager.EvalResult(model.Hand.HIGH_CARD, lambda: (model.Rank.ACE,))
        high2 = manager.EvalResult(model.Hand.HIGH_CARD, lambda: (model.Rank.ACE,))
        self.assertTrue(high1 == high2)
        self.assertFalse(high1 < high2)
        self.assertFalse(high1 > high2)


class TestEvaluatorManager(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.manager = manager.EvaluatorManager()

    def test_find_four_of_kind(self):
        self._test_hand('Js Jc 2h Jh 2c 3c Jd', model.Hand.FOUR_OF_KIND)

    def test_find_full_house(self):
        self._test_hand('2h 2c 2d 5h Jh Js Jc', model.Hand.FULL_HOUSE)

    def test_find_high_card(self):
        self._test_hand('2h 3c 4d 6c 9s', model.Hand.HIGH_CARD)

    def test_find_straight(self):
        self._test_hand('2h 3c 4d Ac 5d Jc', model.Hand.STRAIGHT)

    def test_find_straight_flush(self):
        self._test_hand('2c 2h 3h 4h Ah 5h Jc', model.Hand.STRAIGHT_FLUSH)

    def test_find_two_pairs(self):
        self._test_hand('2h 2c 5h Jh Jc', model.Hand.TWO_PAIR)

    def test_find_two_pairs_best_teo(self):
        self._test_hand('6c 6d jc 7h 7d Jd', model.Hand.TWO_PAIR)

    def _test_hand(self, cards_str, expected_hand):
        cards = model.Card.parse_cards_line(cards_str)
        best_hand = self.manager.find_best_hand(cards)
        self.assertEqual(expected_hand, best_hand.hand)
