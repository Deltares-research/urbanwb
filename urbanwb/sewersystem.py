import numpy as np
import pandas as pd


# 1.3 Class SewerSystem.
class SewerSystem:
    def __init__(self, swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0, prev_so_mss_t0, q_swds_ow_cap=55.1,
                 q_mss_out_cap=26.3, q_mss_ow_cap=48.1, stor_swds_cap=2, stor_mss_cap=9):
        # state
        # prev_stor_swds --- Storage in the storm water drainage system at the end of the previous time step [mm]
        # prev_so_swds --- Overflow of storm water drainage system during the previous time step [mm]
        # prev_stor_mss --- Storage in the mixed sewer system at the end of the previous time step [mm]
        # prev_so_mss --- Overflow of mixed sewer system during the previous time step [mm]

        self.prev_stor_swds = prev_stor_swds_t0
        self.prev_so_swds = prev_so_swds_t0
        self.prev_stor_mss = prev_stor_mss_t0
        self.prev_so_mss = prev_so_mss_t0

        # properties
        # swds_no_meas_area --- area of storm water drainage system (without a measure) [m^2].
        # mss_no_meas_area --- area of mixed sewer system (without a measure) [m^2].
        # q_swds_ow_cap --- predefined discharge capacity of storm water drainage system.
        # q_mss_out_cap --- predefined discharge capacity of mixed sewer system to WWTP.
        # q_mss_ow_cap --- predefined discharge capacity of storm water drainage system to open water.
        # stor_swds_cap --- predefined storage capacity of storm water drainage system [mm].
        # stor_mss_cap --- predefined storage capacity of mixed sewer system.
        # Note the relationship between q_swds_ow_cap, stor_swds_cap, cp_intstor_cap, rainfall intensity.

        self.swds_no_meas_area = swds_no_meas_area
        self.mss_no_meas_area = mss_no_meas_area
        self.q_swds_ow_cap = q_swds_ow_cap
        self.q_mss_out_cap = q_mss_out_cap
        self.q_mss_ow_cap = q_mss_ow_cap
        self.stor_swds_cap = stor_swds_cap
        self.stor_mss_cap = stor_mss_cap

    def sol(self, pr_no_meas_area, cp_no_meas_area, op_no_meas_area, r_pr_swds, r_cp_swds,
            r_op_swds, r_pr_mss, r_cp_mss, r_op_mss, meas_swds, meas_mss, ow_no_meas_area, tot_meas_area):
        # parameters
        # sum_r_swds --- Total runoff to storm water drainage system during the current time step [mm].
        # r_meas_swds --- Inflow from measure area (if applicable) during current time step [mm]
        # sum_r_mss --- Total runoff to mixed sewer system during the current time step [mm].
        # r_meas_mss --- Inflow from measure area (if applicable) during current time step [mm].
        # q_swds_ow --- Outflow from storm water drainage system to open water [mm]
        # q_mss_out --- Discharge from mixed sewer system to Waste Water Treatment Plant (WWTP)
        # during the current time step [mm]
        # q_mss_ow --- Outflow from mixed sewer system to open water during the current time step [mm]
        # so_sdws --- Overflow of storm water drainage system during the current time step [mm]
        # so_mss --- Overflow of mixed sewer system during the current time step [mm]
        # stor_swds --- Storage in the storm water drainage system at the end of the current time step [mm]
        # stor_mss --- Storage in the mixed sewer system at the end of the current time step [mm]

        if self.swds_no_meas_area == 0:

            sum_r_swds = r_meas_swds = q_swds_ow = so_swds = stor_swds = 0

        else:

            sum_r_swds = (pr_no_meas_area * r_pr_swds + cp_no_meas_area * r_cp_swds + op_no_meas_area * r_op_swds) \
                         / self.swds_no_meas_area
            r_meas_swds = meas_swds * tot_meas_area / self.swds_no_meas_area

            if ow_no_meas_area == 0:
                q_swds_ow = min(self.prev_stor_swds + sum_r_swds + r_meas_swds + self.prev_so_swds, self.q_swds_ow_cap)

                so_swds = max(0,
                              self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - self.stor_swds_cap +
                              self.prev_so_swds)

                stor_swds = max(0, self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - (
                            so_swds - self.prev_so_swds))

            else:
                q_swds_ow = min(self.prev_stor_swds + sum_r_swds + r_meas_swds + 0, self.q_swds_ow_cap)

                so_swds = max(0, self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - self.stor_swds_cap + 0)

                stor_swds = max(0, self.prev_stor_swds + sum_r_swds + r_meas_swds - q_swds_ow - so_swds)

            # update state
            self.prev_stor_swds = stor_swds
            self.prev_so_swds = so_swds

        if self.mss_no_meas_area == 0:

            sum_r_mss = r_meas_mss = q_mss_out = q_mss_ow = so_mss = stor_mss = 0

        else:
            sum_r_mss = (pr_no_meas_area * r_pr_mss + cp_no_meas_area * r_cp_mss + op_no_meas_area * r_op_mss) \
                        / self.mss_no_meas_area
            r_meas_mss = meas_mss * tot_meas_area / self.mss_no_meas_area

            if ow_no_meas_area == 0:
                q_mss_out = min(self.prev_stor_mss + sum_r_mss + r_meas_mss + self.prev_so_mss, self.q_mss_out_cap)

                q_mss_ow = max(0, min(self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out + self.prev_so_mss,
                               self.q_mss_ow_cap - self.q_mss_out_cap))

                so_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow - self.stor_mss_cap
                             + self.prev_so_mss)

                stor_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow -
                               (so_mss - self.prev_so_mss))

            else:
                q_mss_out = min(self.prev_stor_mss + sum_r_mss + r_meas_mss + 0, self.q_mss_out_cap)

                q_mss_ow = max(0, min(self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out + 0,
                                      self.q_mss_ow_cap - self.q_mss_out_cap))

                so_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow - self.stor_mss_cap
                             + 0)

                stor_mss = max(0, self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out - q_mss_ow - so_mss)

            # update state
            self.prev_stor_mss = stor_mss
            self.prev_so_mss = so_mss
        return sum_r_swds, r_meas_swds, sum_r_mss, r_meas_mss, q_swds_ow, q_mss_out, q_mss_ow, so_swds, so_mss, \
            stor_swds, stor_mss
