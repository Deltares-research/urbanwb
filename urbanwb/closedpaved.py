#! /usr/bin/env python
# -*- coding: utf-8 -*-


class ClosedPaved:
    """
    Creates an instance of ClosedPaved class with given initial states and properties, iterates sol() function to
    compute states and fluxes of closed paved at each time step.

    Args:
        intstor_cp_t0 (float): initial interception storage on closed paved (at t=0) [mm]
        cp_no_meas_area (float): area of closed paved without measure [m^2]
        cp_meas_area (float): area of closed paved with measure [m^2]
        cp_meas_inflow_area (float): measure inflow area from closed paved, i.e. runoff inflow area to measure from \
        closed paved (>= area of closed paved with measure and <= total area of closed paved) [m^2]
        intstorcap_cp (float): predefined interception storage capacity on closed paved [mm]
        swds_frac (float): part of urban paved area with storm water drainage system (SWDS) [-]
        discfrac_cp (float): part of closed paved that is disconnected from sewer system [-]
    """

    def __init__(
        self,
        intstor_cp_t0,
        cp_no_meas_area,
        cp_meas_area,
        cp_meas_inflow_area,
        intstorcap_cp=1.6,
        swds_frac=1.0,
        discfrac_cp=0.0,
        **kwargs
    ):
        """
        Creates an instance of ClosedPaved class.
        """

        # state

        # self.intstor_cp_prevt (float): interception storage on closed paved at previous time step [mm]
        self.intstor_cp_prevt = intstor_cp_t0

        # properties

        self.cp_no_meas_area = cp_no_meas_area
        self.cp_meas_area = cp_meas_area
        self.cp_meas_inflow_area = cp_meas_inflow_area
        self.intstorcap_cp = intstorcap_cp
        self.swds_frac = swds_frac

        # self.mss_frac (float): part of urban paved area with mixed sewer system (MSS) [-]
        self.mss_frac = 1.0 - self.swds_frac
        self.discfrac_cp = discfrac_cp

        # self.inflowfac_cp (float): measure inflow factor of closed paved [-]
        self.inflowfac_cp = self.inflowfac()

    def inflowfac(self):
        """
        Calculates measure inflow factor of closed paved.

        Returns:
            (float): Measure inflow factor of closed paved.

            * **inflowfac** -- measure inflow factor is calculated as (runoff inflow area to measure from closed paved \
            - area of closed paved with measure) / area of closed paved without measure
        """

        if self.cp_no_meas_area != 0.0:
            return (self.cp_meas_inflow_area - self.cp_meas_area) / self.cp_no_meas_area
        else:
            return 0.0

    def sol(self, p_atm, e_pot_ow):
        """
        Calculates states and fluxes on closed paved during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of closed paved during current time step:

            * **int_cp** -- Interception storage on closed paved after rainfall at the beginning of current time step [mm]
            * **e_atm_cp** -- Evaporation from interception storage on closed paved during current time step [mm]
            * **intstor_cp** -- Remaining interception storage on closed paved at the end of current time step [mm]
            * **r_cp_meas** -- Runoff from closed paved to measure during current time step (not necessarily on closed paved itself) [mm]
            * **r_cp_swds** -- Runoff from closed paved to storm water drainage system (SWDS) during current time step [mm]
            * **r_cp_mss** -- Runoff from closed paved to combined sewer system (MSS) during current time step [mm]
            * **r_cp_up** -- Runoff from closed paved to unpaved during current time step [mm]
        """

        if self.cp_no_meas_area == 0.0:
            int_cp = (
                e_atm_cp
            ) = intstor_cp = r_cp_meas = r_cp_swds = r_cp_mss = r_cp_up = 0.0

        else:
            int_cp = min(self.intstorcap_cp, max(0.0, self.intstor_cp_prevt + p_atm))

            e_atm_cp = min(e_pot_ow, int_cp)

            intstor_cp = int_cp - e_atm_cp

            r_cp_meas = self.inflowfac_cp * max(
                0.0, (p_atm - e_atm_cp - (intstor_cp - self.intstor_cp_prevt))
            )

            r_cp_swds = (
                self.swds_frac
                * (1.0 - self.discfrac_cp)
                * max(
                    0.0,
                    p_atm - e_atm_cp - (intstor_cp - self.intstor_cp_prevt) - r_cp_meas,
                )
            )

            r_cp_mss = (
                self.mss_frac
                * (1.0 - self.discfrac_cp)
                * max(
                    0.0,
                    p_atm - e_atm_cp - (intstor_cp - self.intstor_cp_prevt) - r_cp_meas,
                )
            )

            r_cp_up = self.discfrac_cp * max(
                0.0, p_atm - e_atm_cp - (intstor_cp - self.intstor_cp_prevt) - r_cp_meas
            )

            # update state
            self.intstor_cp_prevt = intstor_cp

        return {
            "int_cp": int_cp,
            "e_atm_cp": e_atm_cp,
            "intstor_cp": intstor_cp,
            "r_cp_meas": r_cp_meas,
            "r_cp_swds": r_cp_swds,
            "r_cp_mss": r_cp_mss,
            "r_cp_up": r_cp_up,
        }
