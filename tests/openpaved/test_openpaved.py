import unittest
from openpaved import OpenPaved


class TestOpenPaved(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        print('setupClass')

    @ classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        """runs the code before every single test"""
        print('Setup')
        # added here.
        self.op_1 = OpenPaved(0, 481.6093594, 0, 0, intstorcap_op=1.6, stormfrac_op=1.0, discfrac_op=0.0)
        # self.op_2 = OpenPaved()
        # not applicable for the time being.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the OpenPaved class. Better carefully select values that can coverage all the
        process threshold"""
        # op_1 --- default setting
        # op_2 --- setting 2
        # op_3 --- setting 3
        # not applicable for now

        # time level t = 12/23/1990 6:00
        self.op_1.init_intstor_op = 0  # update state
        self.assertEqual(self.op_1.sol(2.286, 0.02145677, 1/24)[0], 1.6)

        # time level t = 12/23/1990 7:00
        self.op_1.init_intstor_op = 0.02145677  # update state
        self.assertEqual(self.op_1.sol(12.7, 0.183915171, 1/24)[1], 0.183915171)

    def test_inflowfac(self):
        """test the 'inflowfac' in the PavedRoof class. Actually not very necessary as it is already included in sol"""

        self.assertEqual(self.op_1.inflowfac(), 0)


if __name__ == '__main__':
    unittest.main()
