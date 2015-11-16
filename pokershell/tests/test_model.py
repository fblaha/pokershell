import pickle
import unittest

import pokershell.model as model


class TestRank(unittest.TestCase):
    def test_rank_cmp(self):
        self.assertTrue(model.Rank.ACE >= model.Rank.FOUR)
        self.assertTrue(model.Rank.ACE == model.Rank.ACE)
        self.assertTrue(model.Rank.DEUCE < model.Rank.FOUR)
        self.assertTrue(model.Rank.EIGHT != model.Rank.ACE)


class TestCard(unittest.TestCase):
    def test_parse(self):
        self.assertIn(repr(model.Card.parse('js')), ['J♠', 'Js'])
        self.assertIn(repr(model.Card.parse('Jc')), ['J♣', 'Jc'])
        self.assertIn(repr(model.Card.parse('2c')), ['2♣', '2c'])

    def test_parse_negative(self):
        self.assertRaises(ValueError, model.Card.parse, 'Xs')
        self.assertRaises(ValueError, model.Card.parse, 'Jx')

    def test_eq(self):
        c1 = model.Card.parse('js')
        c2 = model.Card.parse('Js')
        self.assertEqual(c1, c2)
        self.assertEqual(1, len({c1, c2}))

    def test_memento(self):
        c1 = model.Card.parse('js')
        c2 = model.Card.parse('Js')
        self.assertEqual(id(c1), id(c2))

    def test_pickle(self):
        orig = model.Card.parse('9s')
        loaded = pickle.loads(pickle.dumps(orig))
        self.assertEqual(orig, loaded)

    def test_hole_hand_combinations(self):
        all_cards = model.Card.all_cards()
        count = len(list(model.Card.all_combinations(all_cards, 2)))
        self.assertEqual(1326, count)


class TestDeck(unittest.TestCase):
    def test_shuffle(self):
        deck = model.Deck()
        deck.shuffle()
        print(deck)

    def test_pop(self):

        def all_cards():
            deck = model.Deck()
            while True:
                card = deck.pop()
                if card:
                    yield card
                else:
                    break

        self.assertEqual(52, len(set(all_cards())))

    def test_pickle(self):
        orig = model.Deck()
        orig.shuffle()
        dump = pickle.dumps(orig)
        loaded = pickle.loads(dump)
        self.assertEqual(orig, loaded)
