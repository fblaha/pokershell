import testtools

import minsk
import minsk.eval.manager
import minsk.tests.eval.common as common
import minsk.model as model


class TestEvaluatorManager(testtools.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.manager = minsk.eval.manager.EvaluatorManager()

    def test_find_four_of_kind(self):
        self._test_hand('Js Jc 2h Jh 2c 3c Jd', model.Hand.FOUR_OF_KIND)

    def test_find_full_house(self):
        self._test_hand('2h 2c 2d 5h Jh Js Jc', model.Hand.FULL_HOUSE)

    def _test_hand(self, cards_str, expected_hand):
        combo = self.parse_combo(cards_str)
        best_hand = self.manager.find_best_hand(*combo)
        self.assertEqual(expected_hand, best_hand[0])
