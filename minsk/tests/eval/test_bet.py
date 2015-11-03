import testtools

import minsk.eval.bet as bet


class TestBetAdviser(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.adviser = bet.BetAdviser()

    def test_equity(self):
        self._test_func(self.adviser.get_equity)

    def test_max_bet(self):
        self._test_func(self.adviser.get_max_bet)

    def _test_func(self, func):
        self.assertTrue(func(0.3, 100) < 100)
        self.assertTrue(func(0.1, 100) <
                        func(0.2, 100) <
                        func(0.3, 100) <
                        func(0.4, 100) <
                        func(0.5, 100) <
                        func(0.6, 100))
