import testtools

import minsk.shell as shell
import minsk.config as config


class TestLineParser(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.parse = shell.LineParser.parse_state
        self.validate = shell.LineParser.validate_line

    def test_parse_state(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d')
        self.assertEqual(2, parsed.player_num)
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d 7')
        self.assertEqual(7, parsed.player_num)
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d 7 100')
        self.assertEqual(7, parsed.player_num)
        self.assertEqual(100, parsed.pot)

    def test_parse_state_float(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d 7 0.24')
        self.assertEqual(7, parsed.player_num)
        self.assertEqual(0.24, parsed.pot)

    def test_parse_state_chunks(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 8 0.14; 7d 7 0.24; ')
        self.assertEqual(7, parsed.player_num)
        self.assertEqual(0.24, parsed.pot)

    def test_parse_state_empty_chunks(self):
        line = 'As 6c Ad 8s Ac 6d 8 0.14; 7d 7 0.24'
        self.assertEqual(self.parse(line), self.parse(line + ';'))
        self.assertEqual(self.parse(line), self.parse(line + ' ;'))
        self.assertEqual(self.parse(line), self.parse(line + '; '))
        self.assertEqual(self.parse(line), self.parse(line + '; ;; '))

    def test_parse_state_cards(self):
        parsed = self.parse('As 6c Ad 8s Ac 6d 7d')
        self.assertEqual(7, len(parsed.cards))
        parsed = self.parse('As6c Ad8sAc 6d 7d')
        self.assertEqual(7, len(parsed.cards))

    def test_validate(self):
        self.assertTrue(self.validate('As6c Ad8sAc 6d 7d'))
        self.assertTrue(self.validate('As6c Ad8sAc 3 3.0'))
        self.assertTrue(self.validate('As6c; Ad 8s Ac 3 3.0'))

    def test_validate_negative(self):
        self.assertFalse(self.validate('As 6cX'))

    def test_parse_stack(self):
        parsed = shell.LineParser.parse_stack('As 6c Ad 8s Ac 6d 8 0.14; 7d 7 0.24; ')
        self.assertEqual(2, len(parsed.stack))
        self.assertEqual(0.24, parsed.current.pot)


class TestShell(testtools.TestCase):
    def setUp(self):
        super().setUp()
        self.shell = shell.MinskShell()

    def test_brute_force(self):
        self.shell.do_brute_force('As 6c Ad 8s Ac 6d 7d')

    def test_pot_equity(self):
        self.shell.do_eval('As 6c 8c 8s qc 6d 7d 5 0.89')

    def test_monte_carlo(self):
        with config.with_config(10000, 5):
            self.shell.do_monte_carlo('As 6s')

    def test_monte_carlo_eval(self):
        with config.with_config(10000, 5):
            self.shell.do_eval('As 6s 5d')

    def test_look_up(self):
        with config.with_config(10000, 5):
            self.shell.do_look_up('As 6s')

    def test_eval(self):
        self.shell.do_eval('As 6c Ad 8s Ac 6d 7d')

    def test_eval_dupl(self):
        self.shell.do_eval('As 6c Ad As Ac 6d 7d')

    def test_eval_unbeatable(self):
        self.shell.do_eval('ad kd jd qd td 5 100; 4 500 3c 4d')

    def test_eval_pre_flop(self):
        self.shell.do_eval('As 6c')

    def test_eval_no_simulator(self):
        self.shell.do_eval('As 6c 8h')

    def test_sim_cycles(self):
        with config.with_config(10000, 5):
            self.shell.do_sim_cycles('30000')
            self.assertEqual(30000, config.sim_cycles)

    def test_player_num(self):
        with config.with_config(10000, 5):
            self.shell.do_player_num('7')
            self.assertEqual(7, config.player_num)
