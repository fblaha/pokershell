import unittest

import pokershell.parser as parser


class TestLineParser(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.parse = parser.LineParser.parse_state
        self.syntax = parser.LineParser.validate_syntax
        self.semantics = parser.LineParser.validate_semantics

    @staticmethod
    def history(line):
        return parser.LineParser.parse_history(line).history

    def test_parse_state(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d')
        self.assertIsNone(parsed.player_num)
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d 7')
        self.assertEqual(7, parsed.player_num)
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d 7 100.')
        self.assertEqual(7, parsed.player_num)
        self.assertEqual(100, parsed.pot)

    def test_parse_state_float(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d 7 0.24')
        self.assertEqual(7, parsed.player_num)
        self.assertEqual(0.24, parsed.pot)

    def test_parse_state_chunks(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 8 0.14 7d 7 0.24 ')
        self.assertEqual(7, parsed.player_num)
        self.assertEqual(0.24, parsed.pot)

    def test_parse_state_cards(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d')
        self.assertEqual(7, len(parsed.cards))
        parsed = self.parse('As6c Ad8sAc 6d 7d')
        self.assertEqual(7, len(parsed.cards))

    def test_semantics_positive(self):
        self.assertFalse(self.semantics('As6c'))
        self.assertFalse(self.semantics('As6c Ad8sAc'))
        self.assertFalse(self.semantics('As6c Ad8sAc 5 '))
        self.assertFalse(self.semantics('As6c Ad8sAc 0.2'))
        self.assertFalse(self.semantics('As6c Ad8sAc 0.2 5'))
        self.assertFalse(self.semantics('As6c Ad8sAc 0.2 5; 2'))

    def test_semantics_dupl_cards(self):
        self.assertEquals(1, self._error_count('AsAs 5 0.5'))

    def test_semantics_two_player_num(self):
        self.assertEquals(1, self._error_count('As 6c 5 4 '))

    def test_semantics_more_errors(self):
        self.assertEquals(2, self._error_count('As 6c 0.6 6.;  4 3'))

    def test_semantics_two_pots(self):
        self.assertEquals(1, self._error_count('As 6c 0.6 2.'))

    def test_semantics_one_card(self):
        self.assertEquals(1, self._error_count('As 5 0.5'))

    def test_semantics_player_num_growth(self):
        self.assertEquals(1, self._error_count('AsAh 3 0.5;5'))

    def test_semantics_pot_fall(self):
        self.assertEquals(1, self._error_count('AsAh 3 0.5;0.1'))

    def _error_count(self, line):
        errors = self.semantics(line)
        print('-' * 20)
        for err in errors:
            print(err)
        return len(errors)

    def test_syntax(self):
        self.assertTrue(self.syntax('As6c Ad8sAc 6d 7d'))
        self.assertTrue(self.syntax('As6c Ad8sAc 3 3.0'))
        self.assertTrue(self.syntax('As6c; Ad 8s Ac 3 3.0'))

    def test_syntax_negative(self):
        self.assertFalse(self.syntax('As 6cX'))

    def test_parse_history(self):
        history = self.history('As 6c Ad 8s Ac 6d 8 0.14; 7d 7 0.24; ')
        self.assertEqual(2, len(history))
        self.assertEqual(0.24, history[0].pot)
        self.assertEqual(7, history[0].player_num)

    def test_parse_history_state(self):
        history = self.history('2c2d 5d5h6d 3 0.5; 5s ')
        self.assertEqual(2, len(history))
        self.assertEqual(0.5, history[-1].pot)
        self.assertEqual(3, history[-1].player_num)

    def test_parse_history_empty_chunks(self):
        line = 'As 6c Ad 8s Ac 6d 8 0.14; 7d 7 0.24'
        canonical = self.history(line)
        self.assertEqual(canonical, self.history(line + ';'))
        self.assertEqual(canonical, self.history(line + ' ;'))
        self.assertEqual(canonical, self.history(line + '; '))
        self.assertEqual(canonical, self.history(line + '; ;; '))
