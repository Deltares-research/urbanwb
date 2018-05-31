import numpy as np
import pandas as pd
from urbanwb.selector import et_selector, soil_selector
from urbanwb.gwlcalculator import gwlcal
import time

# 1.3 Class Unsaturated zone.
class UnsaturatedZone:
    def __init__(self, theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1):

        # state
        # init_theta_uz --- moisture content at previous time step [mm].
        self.init_theta_uz = theta_uz_t0  # Could also include initial GWL here, or just leave it outside the function.

        # properties
        # uz_no_meas_area --- unsaturated zone area (without a measure) [m^2].
        # uz_meas_area --- unsaturated zone area (with a measure) [m^2].
        # soiltype --- Soil type
        # croptype --- Crop type
        # theta_h3l --- Equilibrium moisture content in rootzone, at which transpiration(Epot≤ 1 mm/d) reduction starts.
        # theta_h3h --- Equilibrium moisture content in rootzone, at which transpiration(Epot≥ 5 mm/d) reduction starts.
        # theta_h1 --- Equilibrium moisture content in rootzone with groundwater level at surface level
        # (top rootzone) (complete saturation).
        # theta_h2 --- Equilibrium moisture content in rootzone with groundwater level at bottom rootzone
        # (field capacity).
        # theta_h4 --- Equilibrium moisture content in rootzone, at which transpiration = 0 (wilting point).
        # k_sat_uz --- Predefined saturated permeability of unsaturated zone.

        self.uz_no_meas_area = uz_no_meas_area
        self.uz_meas_area = uz_meas_area
        self.soiltype = soiltype
        self.croptype = croptype
        et = et_selector(self.soiltype, self.croptype)
        self.theta_h3l = et['theta_h3l_mm'].values
        self.theta_h3h = et['theta_h3h_mm'].values
        self.theta_h1 = et['theta_h1_mm'].values
        self.theta_h2 = et['theta_h2_mm'].values
        self.theta_h4 = et['theta_h4_mm'].values
        self.k_sat_uz = 10 * soil_selector(self.soiltype, self.croptype, 1.5)['k_sat'].values
        # Note here the input gwl (1.5m -MSL) does not affect the K_sat_uz, which is only dependent on soiltype.

    def sol(self, i_up_uz, meas_uz, tot_meas_area, e_ref, prev_gwl, delta_t=1 / 24):

        # parameters
        # i_up_uz --- Infiltration from storage on the surface of the unpaved area
        # to the unsaturated zone during the current time step [mm].
        # r_meas_uz --- Inflow from measure area (if applicable) during current time step [mm]
        # theta_h3_uz --- Equilibrium moisture content in the root zone
        # at which reduction of transpiration starts [mm] for the current time step.
        # t_alpha_uz --- Transpiration factor [-] for the current time step.
        # t_atm_uz --- Transpiration from unsaturated zone to atmosphere during the current time step [mm].
        # gwl_up_uz --- First value in predefined table above groundwater level at the end of previous time step [m-SL].
        # gwl_low_uz --- First value in predefined table below groundwater level at the end of previous time step[m-SL].
        # theta_eq_uz --- Equilibrium soil moisture content in the root zone for the current time step [mm].
        # capris_max_uz --- Maximum capillary rise for the current time step [mm/d].
        # theta_uz --- Soil moisture content in the root zone at the end of the current time step [mm]

        if self.uz_no_meas_area == 0:
            i_up_uz = r_meas_uz = theta_h3_uz = t_alpha_uz = t_atm_uz = gwl_up_uz = gwl_low_uz = theta_eq_uz = \
                      capris_max_uz = p_uz_gw = theta_uz = 0

        else:
            i_up_uz = i_up_uz

            r_meas_uz = meas_uz * tot_meas_area / self.uz_no_meas_area  # May need modifications here?

            if e_ref / (2 * delta_t) < 1:
                theta_h3_uz = self.theta_h3l
            elif e_ref / (2 * delta_t) > 5:
                theta_h3_uz = self.theta_h3h
            else:
                theta_h3_uz = self.theta_h3l + (e_ref / (2 * delta_t) - 1) / 4 * (self.theta_h3h - self.theta_h3l)

            if self.init_theta_uz + i_up_uz + r_meas_uz > self.theta_h1:
                t_alpha_uz = 0
            elif self.init_theta_uz + i_up_uz + r_meas_uz > self.theta_h2:
                t_alpha_uz = 1 - ((self.init_theta_uz + i_up_uz + r_meas_uz) - self.theta_h2) / (
                            self.theta_h1 - self.theta_h2)
            elif self.init_theta_uz + i_up_uz + r_meas_uz > theta_h3_uz:
                t_alpha_uz = 1
            elif self.init_theta_uz + i_up_uz + r_meas_uz > self.theta_h4:
                t_alpha_uz = ((self.init_theta_uz + i_up_uz + r_meas_uz) - self.theta_h4) / (
                            theta_h3_uz - self.theta_h4)
            else:
                t_alpha_uz = 0

            t_atm_uz = e_ref * t_alpha_uz

            gwl_up_uz = gwlcal(prev_gwl)[0]
            gwl_low_uz = gwlcal(prev_gwl)[1]

            if prev_gwl < 10:
                sol_low = soil_selector(self.soiltype, self.croptype, gwl_low_uz)
                sol_up = soil_selector(self.soiltype, self.croptype, gwl_up_uz)
                theta_eq_uz = sol_low['moist_cont_eq_rz[mm]'].values + (
                            gwl_low_uz - prev_gwl) / (gwl_low_uz - gwl_up_uz) * (
                                          sol_up[
                                              'moist_cont_eq_rz[mm]'].values -
                                          sol_low[
                                              'moist_cont_eq_rz[mm]'].values)
                capris_max_uz = sol_low['capris_max[mm/d]'].values + (
                            gwl_low_uz - prev_gwl) / (gwl_low_uz - gwl_up_uz) * (
                                            sol_up[
                                                'capris_max[mm/d]'].values -
                                            sol_low[
                                                'capris_max[mm/d]'].values)
            else:
                sol_10 = soil_selector(self.soiltype, self.croptype, 10)
                theta_eq_uz = sol_10['moist_cont_eq_rz[mm]'].values
                capris_max_uz = sol_10['capris_max[mm/d]'].values

            if self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz > theta_eq_uz:
                p_uz_gw = min(self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz - theta_eq_uz,
                              delta_t * self.k_sat_uz)
            else:
                p_uz_gw = -1 * min(theta_eq_uz - (self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz),
                                   delta_t * capris_max_uz)

            theta_uz = self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz - p_uz_gw

            # update state
            self.init_theta_uz = theta_uz

        return i_up_uz, r_meas_uz, theta_h3_uz, t_alpha_uz, t_atm_uz, gwl_up_uz, gwl_low_uz, theta_eq_uz, \
            capris_max_uz, p_uz_gw, theta_uz
