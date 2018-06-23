import unittest
from urbanwb.closedpaved import ClosedPaved


class TestClosedPaved(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        print('setupClass')

    @ classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        """runs the code before every single test"""
        print('Setup')

        self.cp_1 = ClosedPaved(0, 803.3906406, 0, 0, intstorcap_cp=1.6, stormfrac_cp=1.0, discfrac_cp=0.0)
        # self.cp_2 = ClosedPaved()
        # not applicable for the time being.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the PavedRoof class. Better carefully select values that can coverage all the
        process threshold"""
        # cp_1 --- default setting
        # cp_2 --- setting 2
        # cp_3 --- setting 3
        # not applicable for now

        # time level t = 4/22/1990 19:00
        self.cp_1.init_intstor_cp = 0  # update state
        self.assertEqual(self.cp_1.sol(8.89, 0.111267176)[0], 1.6)

        # time level t = 4/22/1990 20:00
        self.cp_1.init_intstor_cp = 0.111267176  # update state
        self.assertEqual(self.cp_1.sol(0.254, 0)[1], 0)


if __name__ == '__main__':
    unittest.main()
