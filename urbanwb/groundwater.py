import numpy as np
from urbanwb.selector import soil_selector
from urbanwb.gwlcalculator import gwlcal


class Groundwater:
    """
    creates an instance of groundwater class with given states and properties, iterates sol function at each time step.
    """
    def __init__(self, init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=0, w=100, vc=20000, h_deepgw=21.5,
                 flux=1, soiltype=2, croptype=1):

        # state
        # prev_gwl --- groundwater level at previous time step [m-SL].
        # prev_gwl_sl --- groundwater level above surface level at previous time step [m-SL].

        self.prev_gwl = init_gwl_t0
        self.prev_gwl_sl = 0

        # properties
        # gw_no_meas_area --- groundwater area (without a measure) [m^2].
        # gw_meas_area --- groundwater area (with a measure) [m^2].
        # seep_def --- seepage defined by deep groundwater level and flow resistance [0=flux; 1=level].
        # w --- groundwater drainage resistance [d].
        # vc --- flow resistance between deep and shallow groundwater [d].
        # h_deepgw --- defined hydraulic head of deep groundwater [m-SL].
        # flux --- defined constant downward seepage flux [mm/d]
        # soiltype --- soil type
        # croptype --- crop type
        # soil_prm --- soil parameter database determined by soil type and crop type.

        self.gw_no_meas_area = gw_no_meas_area
        self.gw_meas_area = gw_meas_area
        self.seep_def = seep_def
        self.w = w
        self.vc = vc
        self.h_deepgw = h_deepgw
        self.flux = flux
        self.soiltype = soiltype
        self.croptype = croptype
        self.soil_prm = soil_selector(self.soiltype, self.croptype)

    def sol(self, p_uz_gw, uz_no_meas_area, p_op_gw, op_no_meas_area, tot_meas_area, meas_gw,
            prev_owl,  delta_t=1/24):

        # parameter
        # sum_p_gw --- Total percolation from unsaturated zone and from open paved area to groundwater
        # during the current time step [mm].
        # r_meas_gw --- Inflow from measure area (if applicable) during current time step [mm]
        # sc_gw --- Storage coefficient of the groundwater for the current time step [-].
        # h_gw --- Groundwater level at the end of the current time step [m-SL].
        # prev_owl --- Open water level at the previous time step [m-SL].
        # s_gw_out --- downward seepage flux to deep groundwater during current time step [mm].
        # d_gw_ow  --- Groundwater drainage to the open water for the current time step [mm].
        # gwl --- Groundwater level below surface level at the end of the current time step [m-SL].
        # gwl_sl --- Groundwater level above surface level at the end of the current time step [m-SL].

        if self.gw_no_meas_area == 0:
            sum_p_gw = r_meas_gw = gwl_up = gwl_low = sc_gw = h_gw = s_gw_out = d_gw_ow = gwl = gwl_sl = 0
        else:
            sum_p_gw = (p_uz_gw * uz_no_meas_area + p_op_gw * op_no_meas_area) / self.gw_no_meas_area

            r_meas_gw = meas_gw * tot_meas_area / self.gw_no_meas_area

            gwl_sol = gwlcal(self.prev_gwl)
            gwl_up = gwl_sol[0]
            gwl_low = gwl_sol[1]
            id1 = gwl_sol[2]
            id2 = gwl_sol[3]

            if self.prev_gwl < 10:
                sc_gw = self.soil_prm[id2]['stor_coef'] + \
                    (gwl_low - self.prev_gwl) / (gwl_low - gwl_up) * (
                        self.soil_prm[id1]['stor_coef'] -
                        self.soil_prm[id2]['stor_coef'])
            else:
                sc_gw = self.soil_prm[29]['stor_coef']

            if self.seep_def > 0.5:
                h_gw = -(((sum_p_gw + r_meas_gw) / 1000 * self.w * self.vc - self.h_deepgw * self.w - prev_owl *
                          self.vc) / (self.w + self.vc) + (-(self.prev_gwl + self.prev_gwl_sl) -
                         ((sum_p_gw + r_meas_gw) / 1000 * self.w * self.vc - self.h_deepgw * self.w - prev_owl *
                             self.vc) / (self.w + self.vc)) * np.exp(- delta_t * (self.w + self.vc) /
                                                                                 (sc_gw * self.w * self.vc)))

                s_gw_out = 1000 * (
                            self.h_deepgw - 0.5 * (h_gw + (self.prev_gwl + self.prev_gwl_sl))) / self.vc * delta_t

            else:
                h_gw = - (self.w * (((sum_p_gw + r_meas_gw) - self.flux) / 1000) - prev_owl + (
                        -(self.prev_gwl + self.prev_gwl_sl) - (
                            self.w * (((sum_p_gw + r_meas_gw) - self.flux) / 1000) - prev_owl)) * np.exp(
                    - delta_t / (sc_gw * self.w)))

                s_gw_out = delta_t * self.flux

            d_gw_ow = sum_p_gw + r_meas_gw - s_gw_out - sc_gw * (self.prev_gwl + self.prev_gwl_sl - h_gw) * 1000

            gwl = max(0, self.prev_gwl - (sum_p_gw + r_meas_gw - s_gw_out - d_gw_ow) / (1000 * sc_gw))

            gwl_sl = -1 * max(0, (0 - (self.prev_gwl - (sum_p_gw + r_meas_gw - s_gw_out - d_gw_ow) / (1000 * sc_gw)))
                              * sc_gw)

            # update state
            self.prev_gwl = gwl
            self.prev_gwl_sl = gwl_sl

        return {'sum_p_gw': sum_p_gw, 'r_meas_gw': r_meas_gw, 'gwl_up_1': gwl_up, 'gwl_low_1': gwl_low, 'sc_gw': sc_gw,
                'h_gw': h_gw, 's_gw_out': s_gw_out, 'd_gw_ow': d_gw_ow, 'gwl': gwl, 'gwl_sl': gwl_sl}
