player_num = 2
# TODO simulator specific configuration
sim_cycle = 1
hand_stats = 3


def get_config_properties():
    return {k: type(v) for k, v in globals().items()
            if not k.startswith('__') and not callable(v)}
