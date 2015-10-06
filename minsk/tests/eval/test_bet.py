import testtools

import minsk.eval.bet as bet


class TestBetAdviser(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.adviser = bet.BetAdviser()

    def test_max_bet(self):
        self.assertTrue(self.adviser.get_max_bet(0.3, 100) < 100)
        self.assertTrue(self.adviser.get_max_bet(0.1, 100) <
                        self.adviser.get_max_bet(0.2, 100) <
                        self.adviser.get_max_bet(0.3, 100) <
                        self.adviser.get_max_bet(0.4, 100) <
                        self.adviser.get_max_bet(0.5, 100) <
                        self.adviser.get_max_bet(0.6, 100))

    def test_max_bet_flop(self):
        self._test_max_bet_flop(0.1)
        self._test_max_bet_flop(0.3)
        self._test_max_bet_flop(0.5)
        self._test_max_bet_flop(0.7)
        self._test_max_bet_flop(0.9)

    def _test_max_bet_flop(self, strength):
        self.assertTrue(self.adviser.get_max_bet(strength, 100) >
                        self.adviser.get_max_bet(strength, 100, 5))
