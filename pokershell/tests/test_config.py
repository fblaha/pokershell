import unittest

import pokershell.config as config


class TestConfig(unittest.TestCase):
    def test_property(self):
        config.register_option('sample-option', int, 5, 'p', 'test option')
        options = config.options
        print(options)
        self.assertIn('sample-option', options)
