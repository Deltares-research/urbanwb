import unittest
from sewersystem import SewerSystem


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
        # added here. (swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0,
        #                  prev_so_mss_t0, q_swds_ow_cap=55.1, q_mss_out_cap=26.3, q_mss_ow_cap=48.1, stor_swds_cap=2,
        #                  stor_mss_cap=9)
        self.ss_1 = SewerSystem(2845, 0, 0, 0, 0, 0, q_swds_ow_cap=55.1, q_mss_out_cap=26.3, q_mss_ow_cap=48.1,
                                stor_swds_cap=2, stor_mss_cap=9)
        # self.ss_2 = SewerSystem()
        # not applicable for now.

    def tearDown(self):
        """runs the code after every single test"""
        print('tearDown\n')

    def test_sol(self):
        """test the 'sol' in the SewerSystem class. Better carefully select values that can coverage all the
        process threshold"""
        # ss_1 --- default setting
        # ss_2 --- setting 2
        # not applicable for now

        # (pr_no_meas_area, cp_no_meas_area, op_no_meas_area, r_pr_swds, r_cp_swds, r_op_swds, r_pr_mss,
        # r_cp_mss, r_op_mss, meas_swds, meas_mss, ow_no_meas_area, tot_meas_area):

        # time level t = 1/4/1986 11:00
        self.ss_1.prev_stor_swds = 0
        self.ss_1.prev_so_swds = 0
        self.ss_1.prev_stor_mss = 0
        self.ss_1.prev_so_mss = 0
        self.assertAlmostEqual(self.ss_1.sol(1560, 803.390641, 481.6093594, 6.766687196, 6.766687196, 6.725020529,
                                             0, 0, 0, 0, 0, 300, 0)[0], 6.7596337490, places=8)

        # # time level t = 1/4/1986 12:00
        self.ss_1.prev_stor_swds = 0
        self.ss_1.prev_so_swds = 0
        self.ss_1.prev_stor_mss = 0
        self.ss_1.prev_so_mss = 0
        self.assertAlmostEqual(self.ss_1.sol(1560, 803.390641, 481.6093594, 0.670687196, 0.670687196, 0.629020529, 0, 0,
                                             0, 0, 0, 300, 0)[4], 0.663633749, places=8)