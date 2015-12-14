import unittest

import pokershell.config as config
import pokershell.eval.simulation as simulation
import pokershell.shell as shell


class TestShell(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.shell = shell.PokerShell()
        self._player_num = config.player_num
        self._sim_cycle = simulation.MonteCarloSimulator.sim_cycle

    def tearDown(self):
        config.player_num = self._player_num
        config.sim_cycle = self._sim_cycle
        return super().tearDown()

    def test_brute_force(self):
        self.shell.do_eval_brute_force('As 6c Ad 8s Ac 6d 7d')

    def test_pot_equity(self):
        self.shell.do_eval('As 6c 8c 8s qc 6d 7d 5 0.89')

    def test_history(self):
        self.shell.do_eval('As 6c 6 0.2; 8c 8s qc 3 0.4; 6d 0.8;  7d 2 2.5')

    def test_monte_carlo(self):
        self.shell.do_eval_monte_carlo('As 6s')

    def test_monte_carlo_eval(self):
        self.shell.do_eval('As 6s 5d 5')

    def test_look_up(self):
        self.shell.do_eval_look_up('As 6s 5')

    def test_eval(self):
        self.shell.do_eval('As 6c Ad 8s Ac 6d 7d')

    def test_eval_dupl(self):
        self.shell.do_eval('As 6c Ad As Ac 6d 7d')

    def test_eval_unbeatable(self):
        self.shell.do_eval('ad kd jd qd td 5 100.; 4 500. 3c 4d')

    def test_eval_pre_flop(self):
        self.shell.do_eval('As 6c')

    def test_eval_no_simulator(self):
        self.shell.do_eval('As 6c 8h')

    def test_simulator_list(self):
        self.shell.do_simulator_list('')

    def test_simulator_show(self):
        self.shell.do_simulator_show(simulation.MonteCarloSimulator.name)

    def test_option_show(self):
        self.shell.do_option_show('sim-cycle')

    def test_intro_show(self):
        self.shell.do_intro_show('sim-cycle')

    def test_option_list(self):
        self.shell.do_option_list('')

    def test_sim_cycle(self):
        self.shell.do_option_set('sim-cycle 33')
        self.assertEqual(33, simulation.MonteCarloSimulator.sim_cycle.value)

    def test_player_num(self):
        self.shell.do_option_set('player-num 5')
        self.assertEqual(5, config.player_num.value)
