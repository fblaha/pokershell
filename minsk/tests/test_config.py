import testtools

import minsk.config as config


class TestConfig(testtools.TestCase):
    def test_with_config(self):
        orig_sim_cycles = config.sim_cycles
        orig_player_num = config.player_num
        with config.with_config(9999, 20):
            self._check_values(20, 9999)
        self._check_values(orig_player_num, orig_sim_cycles)

    def _check_values(self, expected_player_num, expected_sim_cycles):
        self.assertEqual(expected_sim_cycles, config.sim_cycles)
        self.assertEqual(expected_player_num, config.player_num)

    def test_with_config_default(self):
        orig_sim_cycles = config.sim_cycles
        orig_player_num = config.player_num
        with config.with_config(_sim_cycles=9999):
            self._check_values(orig_player_num, 9999)
        with config.with_config(_player_num=100):
            self._check_values(100, orig_sim_cycles)
        self._check_values(orig_player_num, orig_sim_cycles)
