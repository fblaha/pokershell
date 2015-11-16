import unittest

import pokershell.eval.game as game
import pokershell.model as model

parse = model.Card.parse_cards_line

state = game.GameState


class TestGameState(unittest.TestCase):
    def test_successor_cards(self):
        pre_flop = state(parse('2d 2c'), 5, 100)
        flop = state(parse('2d 2c 4h 5d 8h'), 2, 200)
        self.assertTrue(flop.is_successor(pre_flop))
        self.assertFalse(pre_flop.is_successor(flop))

    def test_successor_player_num(self):
        pre_flop1 = state(parse('2d 2c'), 5, 100)
        pre_flop2 = state(parse('2d 2c'), 2, 200)
        self.assertTrue(pre_flop2.is_successor(pre_flop1))
        self.assertFalse(pre_flop1.is_successor(pre_flop2))

    def test_successor_pot(self):
        pre_flop1 = state(parse('2d 2c'), 5, 100)
        pre_flop2 = state(parse('2d 2c'), 5, 200)
        self.assertTrue(pre_flop2.is_successor(pre_flop1))
        self.assertFalse(pre_flop1.is_successor(pre_flop2))

    def test_successor_eq(self):
        river1 = state(parse('2d 2c 4h 5d 8h 9d jc'), 2, 200)
        river2 = state(parse('2d 2c 4h 5d 8h 9d jc'), 2, 200)
        self.assertFalse(river1.is_successor(river2))

    def test_street(self):
        pre_flop = state(parse('2d 2c'), 5, 100)
        flop = state(parse('2d 2c 4h 5d 8h'), 2, 200)
        turn = state(parse('2d 2c 4h 5d 8h 9d'), 2, 200)
        river = state(parse('2d 2c 4h 5d 8h 9d jc'), 2, 200)
        self.assertEqual(game.Street.PRE_FLOP, pre_flop.street)
        self.assertEqual(game.Street.FLOP, flop.street)
        self.assertEqual(game.Street.TURN, turn.street)
        self.assertEqual(game.Street.RIVER, river.street)

    def test_previous(self):
        pre_flop = state(parse('2d 2c'), 5, 100)
        flop_cards = parse('2d 2c 4h 5d 8h')
        flop = state(flop_cards, 2, 200)
        flop.previous = pre_flop
        self.assertEqual(2, len(flop.history))
        with self.assertRaises(ValueError):
            flop.previous = state(parse('3d 4c'), 5, 100)
            flop.previous = state(flop_cards, 2, 100)
            flop.previous = state(flop_cards, 5, 500)
