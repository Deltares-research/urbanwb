import unittest
from urbanwb.pavedroof import PavedRoof


class TestPavedRoof(unittest.TestCase):
    @ classmethod
    def setUpClass(cls):
        print('setupClass')

    @ classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        """runs the code before every single test"""
        print('Setup')

        self.pr_1 = PavedRoof(0, 1560, 0, 0, intstorcap_pr=1.6, stormfrac_pr=1.0, discfrac_pr=0.0)
        # self.pr_2 = PavedRoof(0, 1560, 0, 0, intstorcap_pr=1.4, stormfrac_pr=0.67, discfrac_pr=0.3)
        # not applicable for the time being.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the PavedRoof class. Better carefully select values that can coverage all the
        process threshold"""
        # pr_1 --- default setting
        # pr_2 --- setting 2
        # pr_3 --- setting 3
        # not applicable for now

        # time level t = 4/20/1990 15:00
        self.pr_1.init_intstor_pr = 0  # update state
        self.assertEqual(self.pr_1.sol(0.508, 0.215938697)[0], 0.508)

        # time level t = 4/20/1990 16:00
        self.pr_1.init_intstor_pr = 0.292061303  # update state
        self.assertEqual(self.pr_1.sol(20.32, 0.215938697)[0], 1.6)


if __name__ == '__main__':
    unittest.main()
