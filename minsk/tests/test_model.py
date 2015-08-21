import pickle

import testtools

from minsk.model import Card, Deck


class TestCard(testtools.TestCase):
    def test_parse(self):
        self.assertEqual('J♠', repr(Card.parse('js')))
        self.assertEqual('J♣', repr(Card.parse('Jc')))
        self.assertEqual('2♣', repr(Card.parse('2c')))

    def test_parse_negative(self):
        self.assertRaises(ValueError, Card.parse, 'Xs')
        self.assertRaises(ValueError, Card.parse, 'Jx')

    def test_eq(self):
        c1 = Card.parse('js')
        c2 = Card.parse('Js')
        self.assertEqual(c1, c2)
        self.assertEqual(1, len({c1, c2}))

    def test_memento(self):
        c1 = Card.parse('js')
        c2 = Card.parse('Js')
        self.assertEqual(id(c1), id(c2))

    def test_pickle(self):
        orig = Card.parse('9s')
        loaded = pickle.loads(pickle.dumps(orig))
        self.assertEqual(orig, loaded)

    def test_cmp_rank(self):
        c1 = Card.parse('js')
        c2 = Card.parse('Qs')
        self.assertTrue(c1 < c2)
        self.assertFalse(c1 > c2)
        self.assertTrue(c1 <= c2)
        self.assertTrue(c1 >= c1)

    def test_cmp_suit(self):
        c1 = Card.parse('qc')
        c2 = Card.parse('Qs')
        self.assertTrue(c1 < c2)
        self.assertFalse(c1 > c2)


class TestDeck(testtools.TestCase):
    def test_shuffle(self):
        deck = Deck()
        deck.shuffle()
        print(deck)

    def test_pop(self):

        def all_cards():
            deck = Deck()
            while True:
                card = deck.pop()
                if card:
                    yield card
                else:
                    break

        self.assertEqual(52, len(set(all_cards())))

    def test_pickle(self):
        orig = Deck()
        orig.shuffle()
        dump = pickle.dumps(orig)
        loaded = pickle.loads(dump)
        self.assertEqual(orig, loaded)
