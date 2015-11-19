import unittest

import pokershell.eval.bet as bet


class TestBetAdviser(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.adviser = bet.BetAdviser()

    def test_equity(self):
        fc = self.adviser.get_equity
        self.assertTrue(fc(0.3, 100) < 100)
        self.assertTrue(fc(0.1, 100) <
                        fc(0.2, 100) <
                        fc(0.3, 100) <
                        fc(0.4, 100) <
                        fc(0.5, 100) <
                        fc(0.6, 100))
