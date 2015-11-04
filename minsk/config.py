import contextlib

player_num = 2
sim_cycle = 1


@contextlib.contextmanager
def with_config(sim_cycle_=None, player_num_=None):
    global sim_cycle, player_num
    if not sim_cycle_:
        sim_cycle_ = sim_cycle
    if not player_num_:
        player_num_ = player_num
    orig_values = sim_cycle, player_num
    sim_cycle, player_num = sim_cycle_, player_num_
    yield
    sim_cycle, player_num = orig_values[0], orig_values[1]
