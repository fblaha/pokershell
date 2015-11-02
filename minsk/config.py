import contextlib
player_num = 2
sim_cycle = 1


@contextlib.contextmanager
def with_config(_sim_cycle=None, _player_num=None):
    global sim_cycle, player_num
    if not _sim_cycle:
        _sim_cycle = sim_cycle
    if not _player_num:
        _player_num = player_num
    orig_values = sim_cycle, player_num
    sim_cycle, player_num = _sim_cycle, _player_num
    yield
    sim_cycle, player_num = orig_values[0], orig_values[1]
