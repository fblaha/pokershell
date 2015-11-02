import testtools

import minsk.config as config


class TestConfig(testtools.TestCase):
    def test_with_config(self):
        orig_sim_cycle = config.sim_cycle
        orig_player_num = config.player_num
        with config.with_config(9999, 20):
            self._check_values(20, 9999)
        self._check_values(orig_player_num, orig_sim_cycle)

    def test_with_config_inner(self):
        orig_sim_cycle = config.sim_cycle
        orig_player_num = config.player_num
        with config.with_config(9999, 20):
            self._check_values(20, 9999)
            with config.with_config(_player_num=21):
                self._check_values(21, 9999)
        self._check_values(orig_player_num, orig_sim_cycle)

    def _check_values(self, expected_player_num, expected_sim_cycle):
        self.assertEqual(expected_sim_cycle, config.sim_cycle)
        self.assertEqual(expected_player_num, config.player_num)

    def test_with_config_default(self):
        orig_sim_cycle = config.sim_cycle
        orig_player_num = config.player_num
        with config.with_config(_sim_cycle=9999):
            self._check_values(orig_player_num, 9999)
        with config.with_config(_player_num=100):
            self._check_values(100, orig_sim_cycle)
        self._check_values(orig_player_num, orig_sim_cycle)
