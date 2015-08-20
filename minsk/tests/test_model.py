import testtools

from minsk.model import Card


class TestCard(testtools.TestCase):
    def test_parse(self):
        self.assertEqual('J♠', str(Card.parse('js')))
        self.assertEqual('J♣', str(Card.parse('Jc')))
        self.assertEqual('2♣', str(Card.parse('2c')))

    def test_parse_negative(self):
        self.assertRaises(ValueError, Card.parse, 'Xs')
        self.assertRaises(ValueError, Card.parse, 'Jx')

    def test_eq(self):
        c1 = Card.parse('js')
        c2 = Card.parse('Js')
        self.assertEqual(c1, c2)
        self.assertEqual(1, len({c1, c2}))
