import unittest

from chintzy.input import InputSource
from chintzy.phase2 import Phase2

class TestPhase2(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_phase2(self):
        ph2 = Phase2(InputSource('<string>', ''))
        assert [c for _, c in ph2.iter(one_more=True)] == ['\n', '']

        for om in [False, True]:
            ph2 = Phase2(InputSource('<string>', '??a???=??/??\'??(??)??!??<??>??-'))
            assert ''.join(c for _, c in ph2.iter(one_more=om)) == '??a?#\\^[]|{}~\n'

            ph2 = Phase2(InputSource('<string>', 'a\\\nb'))
            assert ''.join(c for _, c in ph2.iter(one_more=om)) == 'ab\n'

            ph2 = Phase2(InputSource('<string>', 'a??/\nb'))
            assert ''.join(c for _, c in ph2.iter(one_more=om)) == 'ab\n'

            ph2 = Phase2(InputSource('<string>', ''))
            assert ''.join(c for _, c in ph2.iter(one_more=om)) == '\n'

            ph2 = Phase2(InputSource('<string>', '\\'))
            assert ''.join(c for _, c in ph2.iter(one_more=om)) == '\n'

    def test_span(self):
        ph2 = Phase2(InputSource('<string>', 'a\\\nb'))
        (s1, _), (s2, _), (s3, _) = ph2.iter()
        assert s1.begin.index_in_file == 0
        assert s1.end.index_in_file == 0
        assert s2.begin.index_in_file == 3
        assert s2.end.index_in_file == 3
        assert s3.begin.index_in_file == 4
        assert s3.end.index_in_file == 4

        ph2 = Phase2(InputSource('<string>', '??-'))
        (s1, _), (s2, _) = ph2.iter()
        assert s1.begin.index_in_file == 0
        assert s1.end.index_in_file == 2
        assert s2.begin.index_in_file == 3
        assert s2.end.index_in_file == 3
