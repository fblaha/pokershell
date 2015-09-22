import contextlib

import minsk.config as config
import minsk.model as model
import minsk.eval.context as context


@contextlib.contextmanager
def test_config(sim_cycles, num_player):
    orig_vals = config.sim_cycles, config.player_num
    config.sim_cycles, config.player_num = sim_cycles, num_player
    yield
    config.sim_cycles, config.player_num = orig_vals[0], orig_vals[1]


class TestUtilsMixin:
    def create_context(self, cards_str):
        cards = model.Card.parse_cards(cards_str)
        return context.EvalContext(*cards)
