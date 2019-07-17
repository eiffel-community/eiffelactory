from eiffelactory import dummy

import unittest


class EiffelactoryTestSuite(unittest.TestCase):

    # all tests names must start with "test_"
    def test_dummy_is_true(self):
        assert dummy.dummy()


if __name__ == '__main__':
    unittest.main()
