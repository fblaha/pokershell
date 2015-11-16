import unittest

import pokershell.model as model
import pokershell.tests.eval.common as common


class TestEvalContext(unittest.TestCase, common.TestUtilsMixin):
    def setUp(self):
        super().setUp()
        self.ctx = self.create_context('2h 2c 2d 5h Jh Jc')

    def test_rank_dict(self):
        self.assertEqual(2, len(self.ctx.rank_dict[model.Rank.JACK]))
        self.assertEqual(3, len(self.ctx.rank_dict[model.Rank.DEUCE]))
        self.assertEqual(1, len(self.ctx.rank_dict[model.Rank.FIVE]))
        self.assertEqual(0, len(self.ctx.rank_dict[model.Rank.SEVEN]))

    def test_suit_dict(self):
        self.assertEqual(2, len(self.ctx.suit_dict[model.Suit.CLUBS]))
        self.assertEqual(3, len(self.ctx.suit_dict[model.Suit.HEARTS]))
        self.assertEqual(1, len(self.ctx.suit_dict[model.Suit.DIAMONDS]))

    def test_sorted_ranks(self):
        self.assertEqual([model.Rank.JACK, model.Rank.JACK, model.Rank.FIVE],
                         self.ctx.sorted_ranks[:3])

    def test_complement_ranks(self):
        self.assertEqual([model.Rank.DEUCE],
                         self.ctx.get_complement_ranks(
                             1, model.Rank.JACK, model.Rank.FIVE))
        self.assertEqual([model.Rank.JACK, model.Rank.JACK, model.Rank.DEUCE],
                         self.ctx.get_complement_ranks(3, model.Rank.FIVE))
