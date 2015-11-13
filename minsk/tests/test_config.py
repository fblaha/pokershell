import unittest

import minsk.config as config


class TestConfig(unittest.TestCase):
    def test_property(self):
        config.register_option('sample-option', int, 5, 'p')
        options = config.options
        print(options)
        self.assertIn('sample-option', options)
