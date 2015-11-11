import unittest

import minsk.config as config


class TestConfig(unittest.TestCase):
    def test_property(self):
        properties = config.get_config_properties()
        print(properties)
        self.assertIn('player_num', properties)
