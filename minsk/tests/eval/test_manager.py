import testtools

import minsk.eval.manager as manager
import minsk.tests.eval.common as common
import minsk.model as model


class TestEvaluatorManager(testtools.TestCase, common.TestUtilsMixin):
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

    def _test_hand(self, cards_str, expected_hand):
        cards = model.Card.parse_cards_line(cards_str)
        best_hand = self.manager.find_best_hand(*cards)
        self.assertEqual(expected_hand, best_hand[0])
