class ClosedPaved:
    """
    Creates an instance of ClosedPaved class with given initial states and properties, iterates sol() function at each time step.

    Args:
        self.init_intstor_cp (float): initial interception storage on closed paved area [mm]
        self.cp_no_meas_area (float): closed paved area (without a measure) [m^2]
        self.cp_meas_area (float): closed paved area (with a measure) [m^2]
        self.cp_meas_inflow_area (float): measure inflow area (>= measure area and <= total area) [m^2]
        self.intstorcap (float): predefined storage capacity on closed paved area [mm]
        self.stormfrac (float): part of urban area with storm water drainage system [-]
        self.discfrac (float): part of closed paved area that is disconnected [-]
    """

    def __init__(
        self,
        init_intstor_cp_t0,
        cp_no_meas_area,
        cp_meas_area,
        cp_meas_inflow_area,
        intstorcap_cp=1.6,
        stormfrac_cp=1.0,
        discfrac_cp=0.0,
        **kwargs
    ):
        """
        Creates an instance of ClosedPaved class.
        """

        # state
        # init_intstor_cp_t0 (float): initial interception on closed paved at t=0
        self.init_intstor_cp = init_intstor_cp_t0

        # properties
        self.cp_no_meas_area = cp_no_meas_area
        self.cp_meas_area = cp_meas_area
        self.cp_meas_inflow_area = cp_meas_inflow_area
        self.intstorcap = intstorcap_cp
        self.stormfrac = stormfrac_cp
        # self.mxdfrac (float): part of urban area with mixed sewer system [-]
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_cp

    def inflowfac(self):
        """
        Calculates measure inflow factor of closed paved area (without a measure).

        Returns:
            (float): Measure inflow factor.

            * **inflowfac** -- measure inflow factor is (measure inflow area - measure area) / closed paved area (without measure)
        """
        return (self.cp_meas_inflow_area - self.cp_meas_area) / self.cp_no_meas_area

    def sol(self, p_atm, e_pot_ow):
        """
        Calculates states and fluxes during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential evaporation of open water during current time step [mm]

        Returns:
            (dictionary): A dictionary of states and fluxes during current time step:

            * **int_cp** -- Interception on closed paved after rainfall during current time step [mm]
            * **e_atm_cp** -- Evaporation from interception storage on closed paved during current time step [mm]
            * **intstor_cp** -- Remaining interception storage on closed paved at the end of the current time step [mm]
            * **r_cp_meas** -- Runoff from closed paved to an area with a drainage measure (not necessarily on the closed paved area itself) [mm]
            * **r_cp_swds** -- Runoff from closed paved to the storm water drainage system [mm]
            * **r_cp_mss** -- Runoff from closed paved to the combined sewer system [mm]
            * **r_cp_up** -- Runoff from closed paved to unpaved area [mm]
        """

        if self.cp_no_meas_area == 0:
            int_cp = (
                e_atm_cp
            ) = intstor_cp = r_cp_meas = r_cp_swds = r_cp_mss = r_cp_up = 0

        else:
            int_cp = min(self.intstorcap, max(0, self.init_intstor_cp + p_atm))

            e_atm_cp = min(e_pot_ow, int_cp)

            intstor_cp = int_cp - e_atm_cp

            r_cp_meas = self.inflowfac() * max(
                0, (p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp))
            )

            r_cp_swds = (
                self.stormfrac
                * (1 - self.discfrac)
                * max(
                    0,
                    p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp) - r_cp_meas,
                )
            )

            r_cp_mss = (
                self.mxdfrac
                * (1 - self.discfrac)
                * max(
                    0,
                    p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp) - r_cp_meas,
                )
            )

            r_cp_up = self.discfrac * max(
                0, p_atm - e_atm_cp - (intstor_cp - self.init_intstor_cp) - r_cp_meas
            )

            # update state
            self.init_intstor_cp = intstor_cp

        return {
            "int_cp": int_cp,
            "e_atm_cp": e_atm_cp,
            "intstor_cp": intstor_cp,
            "r_cp_meas": r_cp_meas,
            "r_cp_swds": r_cp_swds,
            "r_cp_mss": r_cp_mss,
            "r_cp_up": r_cp_up,
        }
