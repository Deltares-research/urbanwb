class PavedRoof:
    """
    Creates an instance of PavedRoof class with given states and properties, iterates sol() function at each time step.

    Args:
        self.init_intstor_pr (float): initial interception storage on paved roof area [mm]
        self.pr_no_meas_area (float): paved roof area (without a measure) [m^2]
        self.pr_meas_area (float): paved roof area (with a measure) [m^2]
        self.pr_meas_inflow_area (float): measure inflow area (>= measure area and <= total area) [m^2]
        self.intstorcap (float): predefined storage capacity on paved roof area [mm]
        self.stormfrac (float): part of urban area with storm water drainage system [-]
        self.mxdfrac (float): part of urban area with mixed sewer system [-]
        self.discfrac (float): part of paved roof area that is disconnected [-]
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
        """
        Creates an instance of PavedRoof class.
        """

        # state
        self.init_intstor_pr = init_intstor_pr_t0

        # properties
        self.pr_no_meas_area = pr_no_meas_area
        self.pr_meas_area = pr_meas_area
        self.pr_meas_inflow_area = pr_meas_inflow_area
        self.intstorcap = intstorcap_pr
        self.stormfrac = stormfrac_pr
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_pr

    def inflowfac(self):
        """
        Calculates measure inflow factor.

        Returns:
            (float): measure inflow factor of paved roof area
        """
        return (self.pr_meas_inflow_area - self.pr_meas_area) / self.pr_no_meas_area

    def sol(self, p_atm, e_pot_ow):
        """
        Calculates storage and fluxes during current time step.

        Args:
            p_atm (float): precipitation during current time step
            e_pot_ow (float): potential evaporation during current time step

        Returns:
            (dictionary): A dictionary of storage and fluxes during current time step:

            * **int_pr** -- Interception on paved roof after rainfall during current time step [mm]
            * **e_atm_pr** -- Evaporation from interception storage on paved roof during current time step [mm]
            * **intstor_pr** -- Remaining interception storage on paved roof at the end of the current time step [mm]
            * **r_pr_meas** -- Runoff from paved roof to an area with a drainage measure (not necessarily on the paved roof itself) [mm]
            * **r_pr_swds** -- Runoff from paved roof to the storm water drainage system [mm]
            * **r_pr_mss** -- Runoff from paved roof to the mixed sewer system [mm]
            * **r_pr_up** -- Runoff from paved roof to unpaved area [mm]
        """

        if self.pr_no_meas_area == 0:
            int_pr = (
                e_atm_pr
            ) = intstor_pr = r_pr_meas = r_pr_swds = r_pr_mss = r_pr_up = 0

        else:
            int_pr = min(self.intstorcap, max(0, self.init_intstor_pr + p_atm))

            e_atm_pr = min(e_pot_ow, int_pr)

            intstor_pr = int_pr - e_atm_pr

            r_pr_meas = self.inflowfac() * max(
                0.0, p_atm - e_atm_pr - (intstor_pr - self.init_intstor_pr)
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
