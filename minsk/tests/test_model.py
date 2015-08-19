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
