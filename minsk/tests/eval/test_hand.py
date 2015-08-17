import testtools

from minsk.eval.hand import HandEval


class TestHandEval(testtools.TestCase):
    def test_eval(self):
        hand_eval = HandEval()
        self.assertEqual(1, hand_eval.eval())
