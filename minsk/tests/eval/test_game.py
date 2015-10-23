import testtools

import minsk.eval.game as game
import minsk.model as model

parse = model.Card.parse_cards_line

state = game.GameState


class TestGameState(testtools.TestCase):
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


class TestGameStack(testtools.TestCase):
    def test_stack(self):
        stack = game.GameStack()
        stack.add_state(state(parse('2d 2c'), 5, 100))
        self.assertEqual(1, len(stack.stack))
        stack.add_state(state(parse('2d 2c 4h 5d 8h'), 2, 200))
        self.assertEqual(2, len(stack.stack))
        stack.add_state(state(parse('3d 4c'), 5, 100))
        self.assertEqual(1, len(stack.stack))
