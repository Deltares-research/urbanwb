from urbanwb.selector import soil_selector


class Unpaved:
    """
    creates an instance of unpaved class with given states and properties, iterates sol function at each time step.
    """
    def __init__(self, fin_stor_up_t0, up_no_meas_area, up_meas_area, up_meas_inflow_area, infilcap_up=48,
                 intstorcap_up=20, soiltype=2, croptype=1):

        # state
        # prev_fin_stor_up --- final storage on the surface of the unpaved area at previous time step [mm].
        self.prev_fin_stor_up = fin_stor_up_t0

        # properties
        # up_no_meas_area --- unpaved area (without a measure) [m^2].
        # up_meas_area --- unpaved area (with a measure) [m^2].
        # up_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # soiltype --- Soil type
        # croptype --- Crop type
        # infilcap_up --- predefined infiltration capacity of unpaved area [mm/d].
        # mois_uz_max --- maximum water volume in root zone [mm].
        # k_sat_uz --- predefined saturated permeability of unsaturated zone [mm/d].
        # intstorcap_up --- predefined storage capacity on unpaved area [mm].

        self.up_no_meas_area = up_no_meas_area
        self.up_meas_area = up_meas_area
        self.up_meas_inflow_area = up_meas_inflow_area
        self.soiltype = soiltype
        self.croptype = croptype
        self.infilcap_up = infilcap_up
        self.intstorcap_up = intstorcap_up
        self.soil_prm = soil_selector(self.soiltype, self.croptype)
        self.mois_uz_max = self.soil_prm[0]['moist_cont_eq_rz[mm]']
        self.k_sat_uz = 10 * self.soil_prm[0]['k_sat']
        self.inflowfac = self.inflowfac()

    def inflowfac(self):
        return (self.up_meas_inflow_area - self.up_meas_area) / self.up_no_meas_area

    def sol(self, p_atm, e_pot_ow, r_pr_up, r_cp_up, r_op_up, prev_mois_uz, pr_no_meas_area, cp_no_meas_area,
            op_no_meas_area, ow_no_meas_area, delta_t=1 / 24):

        # parameters
        # sum_r_up --- Runoff from all paved areas to unpaved area [mm].
        # init_stor_up --- Initial storage on the surface of the unpaved area
        # after rainfall during current time step [mm]
        # act_infilcap_up --- Actual infiltration capacity during the current time step [mm].
        # prev_mois_uz --- water volume in root zone at the previous time step [mm].
        # tfac_up --- Time factor [-]. Part of the current time step that storage on the surface of the unpaved area
        # is available for infiltration and evaporation.
        # e_atm_up --- Evaporation from storage on the surface of the unpaved area during the current time step [mm].
        # i_up_uz --- Infiltration from storage on the surface of the unpaved area [mm].
        # to the unsaturated zone during the current time step [mm].
        # fin_stor_up --- Final storage on the surface of the unpaved area at the end of the current time step [mm].
        # r_up_meas --- Runoff from unpaved to an area with a drainage measure during the current time step [mm].
        # (not necessarily on the unpaved area itself) [mm].
        # r_up_ow --- Runoff from unpaved to open water area during the current time step [mm].

        if self.up_no_meas_area == 0:
            sum_r_up = init_stor_up = act_infilcap_up = tfac_up = e_atm_up = i_up_uz = fin_stor_up \
                     = r_up_meas = r_up_ow = 0

        else:
            sum_r_up = (r_pr_up * pr_no_meas_area + r_cp_up * cp_no_meas_area + r_op_up * op_no_meas_area) / (
                self.up_no_meas_area)

            init_stor_up = self.prev_fin_stor_up + p_atm + sum_r_up

            act_infilcap_up = min(delta_t * self.infilcap_up,
                                  self.mois_uz_max - prev_mois_uz + min(self.mois_uz_max - prev_mois_uz,
                                                                        delta_t * self.k_sat_uz))

            if e_pot_ow + act_infilcap_up <= 0:
                tfac_up = 0
            else:
                tfac_up = min(1, init_stor_up / (e_pot_ow + act_infilcap_up))

            e_atm_up = tfac_up * e_pot_ow

            i_up_uz = tfac_up * act_infilcap_up

            if ow_no_meas_area == 0:
                fin_stor_up = max(0, min(self.intstorcap_up + (self.up_no_meas_area - (
                            self.up_meas_inflow_area - self.up_meas_area)) / self.up_no_meas_area * (
                                                     init_stor_up - e_atm_up - i_up_uz - self.intstorcap_up),
                                         init_stor_up - e_atm_up - i_up_uz))

            else:
                fin_stor_up = max(0, min(self.intstorcap_up, init_stor_up - e_atm_up - i_up_uz))

            r_up_meas = self.inflowfac * max(0, init_stor_up - e_atm_up - i_up_uz - self.intstorcap_up)

            if ow_no_meas_area == 0:
                r_up_ow = 0
            else:
                r_up_ow = max(0, init_stor_up - e_atm_up - i_up_uz - self.intstorcap_up - r_up_meas)

            # update state
            self.prev_fin_stor_up = fin_stor_up

        return {'sum_r_up': sum_r_up, 'init_stor_up': init_stor_up, 'act_infilcap_up': act_infilcap_up,
                'tfac_up': tfac_up, 'e_atm_up': e_atm_up, 'i_up_uz': i_up_uz, 'fin_stor_up': fin_stor_up,
                'r_up_meas': r_up_meas, 'r_up_ow': r_up_ow}
