import unittest

import chintzy
from chintzy.standards import (
        c_std_modules,
        cxx_std_modules,
        all_std_modules,
        named_std_module,
)


class StandardsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_standards(self):
        assert [m.__name__.replace('chintzy.std.', '') for m in c_std_modules()] == ['c89', 'c99', 'c11']
        assert [m.__name__.replace('chintzy.std.', '') for m in cxx_std_modules()] == ['cxx98', 'cxx11', 'cxx14']
        assert [m.__name__.replace('chintzy.std.', '') for m in all_std_modules()] == ['c89', 'c99', 'c11', 'cxx98', 'cxx11', 'cxx14']
        for m in all_std_modules():
            assert m.__name__.startswith('chintzy.std.')
            n = m.__name__.replace('chintzy.std.', '')
            assert named_std_module(n) is m
