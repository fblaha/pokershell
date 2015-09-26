import testtools

import minsk.shell as shell
import minsk.config as config
import minsk.tests.eval.common as common


class TestShell(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.shell = shell.MinskShell()

    def test_brute_force(self):
        self.shell.do_bf('As 6c Ad 8s Ac 6d 7d')

    def test_hybrid_monte_carlo(self):
        with common.test_config(10000, 5):
            self.shell.do_hmc('As 6c Ad 8s Ac 6d 7d')

    def test_monte_carlo(self):
        with common.test_config(10000, 5):
            self.shell.do_mc('As 6s')

    def test_monte_carlo_eval(self):
        with common.test_config(10000, 5):
            self.shell.do_e('As 6s 5d')

    def test_look_up(self):
        with common.test_config(10000, 5):
            self.shell.do_lu('As 6s')

    def test_eval(self):
        self.shell.do_e('As 6c Ad 8s Ac 6d 7d')

    def test_eval_pre_flop(self):
        self.shell.do_e('As 6c')

    def test_eval_no_simulator(self):
        self.shell.do_e('As 6c 8h')

    def test_sim_cycles(self):
        with common.test_config(10000, 5):
            self.shell.do_sim_cycles('30000')
            self.assertEqual(30000, config.sim_cycles)

    def test_player_num(self):
        with common.test_config(10000, 5):
            self.shell.do_player_num('7')
            self.assertEqual(7, config.player_num)
