from urbanwb.selector import et_selector, soil_selector
from urbanwb.gwlcalculator import gwlcal


class UnsaturatedZone:
    """
    creates an instance of unsaturated zone class with given states and properties,
    iterates sol function at each time step.
    """
    def __init__(self, theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1):

        # state
        # init_theta_uz --- moisture content at previous time step [mm].
        self.init_theta_uz = theta_uz_t0

        # properties
        # uz_no_meas_area --- unsaturated zone area (without a measure) [m^2].
        # uz_meas_area --- unsaturated zone area (with a measure) [m^2].
        # soiltype --- Soil type
        # croptype --- Crop type
        # theta_h3l --- Equilibrium moisture content in rootzone, at which transpiration(Epot≤ 1 mm/d) reduction starts.
        # theta_h3h --- Equilibrium moisture content in rootzone, at which transpiration(Epot≥ 5 mm/d) reduction starts.
        # theta_h1 --- Equilibrium moisture content in rootzone with groundwater level at surface level
        # i.e. top root zone (complete saturation).
        # theta_h2 --- Equilibrium moisture content in rootzone with groundwater level at bottom root zone
        # (field capacity).
        # theta_h4 --- Equilibrium moisture content in rootzone, at which transpiration = 0 (wilting point).
        # soil_prm --- soil parameter database determined by soil type and crop type.
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
        self.soil_prm = soil_selector(self.soiltype, self.croptype)
        self.k_sat_uz = 10 * self.soil_prm[0]['k_sat']
        # Note here the predefined index 0 does not affect K_sat_uz, which is only dependent on soiltype.

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
        # theta_uz --- Soil moisture content in the root zone at the end of the current time step [mm].

        if self.uz_no_meas_area == 0:
            i_up_uz = r_meas_uz = theta_h3_uz = t_alpha_uz = t_atm_uz = gwl_up = gwl_low = theta_eq_uz = \
                      capris_max_uz = p_uz_gw = theta_uz = 0

        else:
            i_up_uz = i_up_uz  # It is assumed that UP and UZ areas area equal.

            r_meas_uz = meas_uz * tot_meas_area / self.uz_no_meas_area

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

            gwl_sol = gwlcal(prev_gwl)
            gwl_up = gwl_sol[0]
            gwl_low = gwl_sol[1]
            id1 = gwl_sol[2]
            id2 = gwl_sol[3]

            if prev_gwl < 10:
                theta_eq_uz = self.soil_prm[id2]['moist_cont_eq_rz[mm]'] + (
                            gwl_low - prev_gwl) / (gwl_low - gwl_up) * (
                            self.soil_prm[id1][
                                              'moist_cont_eq_rz[mm]'] -
                            self.soil_prm[id2][
                                              'moist_cont_eq_rz[mm]'])
                capris_max_uz = self.soil_prm[id2]['capris_max[mm/d]'] + (
                            gwl_low - prev_gwl) / (gwl_low - gwl_up) * (
                        self.soil_prm[id1][
                                                'capris_max[mm/d]'] -
                        self.soil_prm[id2][
                                                'capris_max[mm/d]'])
            else:
                theta_eq_uz = self.soil_prm[29]['moist_cont_eq_rz[mm]']
                capris_max_uz = self.soil_prm[29]['capris_max[mm/d]']

            if self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz > theta_eq_uz:
                p_uz_gw = min(self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz - theta_eq_uz,
                              delta_t * self.k_sat_uz)
            else:
                p_uz_gw = -1 * min(theta_eq_uz - (self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz),
                                   delta_t * capris_max_uz)

            theta_uz = self.init_theta_uz + i_up_uz + r_meas_uz - t_atm_uz - p_uz_gw

            # update state
            self.init_theta_uz = theta_uz

        return {'i_up_uz': i_up_uz, 'r_meas_uz': r_meas_uz, 'theta_h3_uz': theta_h3_uz, 't_alpha_uz': t_alpha_uz,
                't_atm_uz': t_atm_uz, 'gwl_up': gwl_up, 'gwl_low': gwl_low, 'theta_eq_uz': theta_eq_uz,
                'capris_max_uz': capris_max_uz, 'p_uz_gw': p_uz_gw, 'theta_uz': theta_uz}
