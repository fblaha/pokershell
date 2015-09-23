import contextlib

import minsk.config as config
import minsk.model as model
import minsk.eval.context as context


@contextlib.contextmanager
def test_config(sim_cycles, num_player):
    orig_values = config.sim_cycles, config.player_num
    config.sim_cycles, config.player_num = sim_cycles, num_player
    yield
    config.sim_cycles, config.player_num = orig_values[0], orig_values[1]


class TestUtilsMixin:
    @staticmethod
    def create_context(cards_str):
        cards = model.Card.parse_cards(cards_str)
        return context.EvalContext(*cards)
