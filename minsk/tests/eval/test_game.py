import testtools

import minsk.eval.game as game
import minsk.model as model


class TestGameState(testtools.TestCase):
    def test_successor_cards(self):
        pre_flop = game.GameState(model.Card.parse_cards_line("2d 2c"), 5, 100)
        flop = game.GameState(model.Card.parse_cards_line("2d 2c 4h 5d 8h"), 2, 200)
        self.assertTrue(flop.is_successor(pre_flop))
        self.assertFalse(pre_flop.is_successor(flop))

    def test_successor_player_num(self):
        pre_flop = game.GameState(model.Card.parse_cards_line("2d 2c"), 5, 100)
        flop = game.GameState(model.Card.parse_cards_line("2d 2c"), 2, 200)
        self.assertTrue(flop.is_successor(pre_flop))
        self.assertFalse(pre_flop.is_successor(flop))

    def test_successor_pot(self):
        pre_flop = game.GameState(model.Card.parse_cards_line("2d 2c"), 5, 100)
        flop = game.GameState(model.Card.parse_cards_line("2d 2c"), 5, 200)
        self.assertTrue(flop.is_successor(pre_flop))
        self.assertFalse(pre_flop.is_successor(flop))
