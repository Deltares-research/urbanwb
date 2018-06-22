class ClosedPaved:
    """
    creates an instance of closed paved class with given states and properties, iterates sol function at each time step.
    """
    def __init__(self, init_intstor_cp_t0, cp_no_meas_area, cp_meas_area, cp_meas_inflow_area, intstorcap_cp=1.6,
                 stormfrac_cp=1.0, discfrac_cp=0.0):

        # state
        # init_intstor_cp --- initial interception storage on closed paved area [mm].
        self.init_intstor_cp = init_intstor_cp_t0

        # properties
        # cp_no_meas_area --- closed paved area (without a measure) [m^2].
        # cp_meas_area --- closed paved area (with a measure) [m^2].
        # cp_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # intstorcap_cp --- predefined storage capacity on closed paved area [mm].
        # stormfrac_cp --- part of urban area with storm water drainage system [-].
        # mxdfrac --- part of urban area with mixed sewer system [-].
        # discfrac_cp --- part of closed paved area that is disconnected [-].

        self.cp_no_meas_area = cp_no_meas_area
        self.cp_meas_area = cp_meas_area
        self.cp_meas_inflow_area = cp_meas_inflow_area
        self.intstorcap = intstorcap_cp
        self.stormfrac = stormfrac_cp
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_cp
        self.inflowfac = self.inflowfac()

    def inflowfac(self):
        return (self.cp_meas_inflow_area - self.cp_meas_area) / self.cp_no_meas_area

    def sol(self, p_atm, e_pot_ow):

        # parameters
        # int_cp --- Interception on closed paved after rainfall during current time step [mm].
        # e_atm_cp --- Evaporation from interception storage on closed paved during current time step [mm].
        # intstor_cp --- Remaining interception storage on closed paved at the end of the current time step [mm].
        # r_cp_meas --- Runoff from closed paved to an area with a drainage measure
        # (not necessarily on the closed paved area itself) [mm].
        # r_cp_swds --- Runoff from closed paved to the storm water drainage system [mm].
        # r_cp_mss --- Runoff from closed paved to the mixed sewer system [mm].
        # r_cp_up --- Runoff from closed paved to unpaved area [mm].

        if self.cp_no_meas_area == 0:
            int_cp = e_atm_cp = intstor_cp = r_cp_meas = r_cp_swds = r_cp_mss = r_cp_up = 0

        else:
            int_cp = min(self.intstorcap, max(0, self.init_intstor_cp + p_atm))

            e_atm_cp = min(e_pot_ow, int_cp)

            intstor_cp = int_cp - e_atm_cp

            r_cp_meas = self.inflowfac * max(0, (p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp)))

            r_cp_swds = self.stormfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_cp - (
                        intstor_cp - self.init_intstor_cp) - r_cp_meas)

            r_cp_mss = self.mxdfrac * (1 - self.discfrac) * max(0, p_atm - e_atm_cp - (
                        intstor_cp - self.init_intstor_cp) - r_cp_meas)

            r_cp_up = self.discfrac * max(0, p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp) - r_cp_meas)

            # update state
            self.init_intstor_cp = intstor_cp

        return {'int_cp': int_cp, 'e_atm_cp': e_atm_cp, 'intstor_cp': intstor_cp, 'r_cp_meas': r_cp_meas,
                'r_cp_swds': r_cp_swds, 'r_cp_mss': r_cp_mss, 'r_cp_up': r_cp_up}
