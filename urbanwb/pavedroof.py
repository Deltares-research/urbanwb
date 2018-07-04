class PavedRoof:
    """
    creates an instance of PavedRoof class with given states and properties, iterates sol function at each time step.
    """

    def __init__(
        self,
        init_intstor_pr_t0,
        pr_no_meas_area,
        pr_meas_area,
        pr_meas_inflow_area,
        intstorcap_pr=1.6,
        stormfrac_pr=1.0,
        discfrac_pr=0.0,
    ):

        # state
        # init_intstor_pr --- initial interception storage on paved roof area [mm].
        self.init_intstor_pr = init_intstor_pr_t0

        # properties
        # pr_no_meas_area --- paved roof area (without a measure) [m^2].
        # pr_meas_area --- paved roof area (with a measure) [m^2].
        # pr_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # intstorcap_pr --- predefined storage capacity on paved roof area [mm].
        # stormfrac_pr --- part of urban area with storm water drainage system [-].
        # self.mxdfrac--- part of urban area with mixed sewer system [-].
        # discfrac_pr --- part of paved roof area that is disconnected [-].

        self.pr_no_meas_area = pr_no_meas_area
        self.pr_meas_area = pr_meas_area
        self.pr_meas_inflow_area = pr_meas_inflow_area
        self.intstorcap = intstorcap_pr
        self.stormfrac = stormfrac_pr
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_pr

    def inflowfac(self):
        return (self.pr_meas_inflow_area - self.pr_meas_area) / self.pr_no_meas_area

    def sol(self, p_atm, e_pot_ow):

        # parameters
        # int_pr --- Interception on paved roof after rainfall during current time step [mm].
        # e_atm_pr --- Evaporation from interception storage on paved roof during current time step [mm].
        # intstor_pr --- Remaining interception storage on paved roof at the end of the current time step [mm].
        # r_pr_meas --- Runoff from paved roof to an area with a drainage measure
        # (not necessarily on the roof itself) [mm].
        # r_pr_swds --- Runoff from paved roof to the storm water drainage system [mm].
        # r_pr_mss --- Runoff from paved roof to the mixed sewer system [mm].
        # r_pr_up --- Runoff from paved roof to unpaved area [mm].

        if self.pr_no_meas_area == 0:
            int_pr = (
                e_atm_pr
            ) = intstor_pr = r_pr_meas = r_pr_swds = r_pr_mss = r_pr_up = 0

        else:
            int_pr = min(self.intstorcap, max(0, self.init_intstor_pr + p_atm))

            e_atm_pr = min(e_pot_ow, int_pr)

            intstor_pr = int_pr - e_atm_pr
            # everytime it will excute inflowfac(), improvements can be made here.
            r_pr_meas = self.inflowfac() * max(
                0, p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr)
            )

            r_pr_swds = (
                self.stormfrac
                * (1 - self.discfrac)
                * max(
                    0,
                    p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr) - r_pr_meas,
                )
            )

            r_pr_mss = (
                self.mxdfrac
                * (1 - self.discfrac)
                * max(
                    0,
                    p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr) - r_pr_meas,
                )
            )

            r_pr_up = self.discfrac * max(
                0, p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr) - r_pr_meas
            )

            # update state
            self.init_intstor_pr = intstor_pr

        return {
            "int_pr": int_pr,
            "e_atm_pr": e_atm_pr,
            "intstor_pr": intstor_pr,
            "r_pr_meas": r_pr_meas,
            "r_pr_swds": r_pr_swds,
            "r_pr_mss": r_pr_mss,
            "r_pr_up": r_pr_up,
        }
