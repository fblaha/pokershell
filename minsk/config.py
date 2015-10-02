import contextlib

player_num = 2
sim_cycles = 40000


@contextlib.contextmanager
def with_config(_sim_cycles=sim_cycles, _player_num=player_num):
    global sim_cycles, player_num
    orig_values = sim_cycles, player_num
    sim_cycles, player_num = _sim_cycles, _player_num
    yield
    sim_cycles, player_num = orig_values[0], orig_values[1]
