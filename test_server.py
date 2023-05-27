import sys
import os
import unittest

from server import start_server


class TestServer(unittest.TestCase):

    def test_parameters_start(self):
        self.assertRaises(NameError, start_server)


if __name__ == '__main__':
    unittest.main()
# python test_server.py
