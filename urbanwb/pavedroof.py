#! /usr/bin/env python
# -*- coding: utf-8 -*-


class PavedRoof:
    """
    Creates an instance of PavedRoof class with given initial states and properties, iterates sol() function to compute
    states and fluxes of paved roof at each time step.

    Args:
        intstor_pr_t0 (float): initial interception storage on paved roof (at t=0) [mm]
        pr_no_meas_area (float): area of paved roof without measure [m^2]
        pr_meas_area (float): area of paved roof with measure [m^2]
        pr_meas_inflow_area (float): measure inflow area from paved roof, i.e. runoff inflow area to measure from paved\
        roof (>= area of paved roof with measure and <= total area of paved roof) [m^2]
        intstorcap_pr (float): predefined interception storage capacity on paved roof [mm]
        swds_frac (float): part of urban paved area with storm water drainage system (SWDS) [-]
        discfrac_pr (float): part of paved roof that is disconnected from sewer system [-]
    """

    def __init__(
        self,
        intstor_pr_t0,
        pr_no_meas_area,
        pr_meas_area,
        pr_meas_inflow_area,
        intstorcap_pr=1.6,
        swds_frac=1.0,
        discfrac_pr=0.0,
        **kwargs
    ):
        """
        Creates an instance of PavedRoof class.
        """

        # state

        # self.intstor_pr_prevt (float): interception storage on paved roof at previous time step [mm]
        self.intstor_pr_prevt = intstor_pr_t0

        # properties

        self.pr_no_meas_area = pr_no_meas_area
        self.pr_meas_area = pr_meas_area
        self.pr_meas_inflow_area = pr_meas_inflow_area
        self.intstorcap_pr = intstorcap_pr
        self.swds_frac = swds_frac

        # self.mss_frac (float): part of urban paved area with mixed sewer system (MSS) [-]
        self.mss_frac = 1.0 - self.swds_frac
        self.discfrac_pr = discfrac_pr

        # self.inflowfac_pr (float): measure inflow factor of paved roof [-]
        self.inflowfac_pr = self.inflowfac()

    def inflowfac(self):
        """
        Calculates measure inflow factor of paved roof.

        Returns:
            (float): Measure inflow factor of paved roof

            * **inflowfac** -- measure inflow factor is calculated as (runoff inflow area to measure from paved roof - \
            area of paved roof with measure) / area of paved roof without measure
        """

        if self.pr_no_meas_area != 0.0:
            return (self.pr_meas_inflow_area - self.pr_meas_area) / self.pr_no_meas_area
        else:
            return 0.0

    def sol(self, p_atm, e_pot_ow):
        """
        Calculates states and fluxes on paved roof during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of paved roof during current time step:

            * **int_pr** -- Interception storage on paved roof after rainfall at the beginning of current time step [mm]
            * **e_atm_pr** -- Evaporation from interception storage on paved roof during current time step [mm]
            * **intstor_pr** -- Remaining interception storage on paved roof at the end of current time step [mm]
            * **r_pr_meas** -- Runoff from paved roof to measure during current time step (not necessarily on paved roof itself) [mm]
            * **r_pr_swds** -- Runoff from paved roof to storm water drainage system (SWDS) during current time step [mm]
            * **r_pr_mss** -- Runoff from paved roof to combined sewer system (MSS) during current time step [mm]
            * **r_pr_up** -- Runoff from paved roof to unpaved during current time step [mm]
        """

        if self.pr_no_meas_area == 0.0:
            int_pr = (
                e_atm_pr
            ) = intstor_pr = r_pr_meas = r_pr_swds = r_pr_mss = r_pr_up = 0.0

        else:
            int_pr = min(self.intstorcap_pr, max(0.0, self.intstor_pr_prevt + p_atm))

            e_atm_pr = min(e_pot_ow, int_pr)

            intstor_pr = int_pr - e_atm_pr

            r_pr_meas = self.inflowfac_pr * max(
                0.0, p_atm - e_atm_pr - (intstor_pr - self.intstor_pr_prevt)
            )

            r_pr_swds = (
                self.swds_frac
                * (1.0 - self.discfrac_pr)
                * max(
                    0.0,
                    p_atm - e_atm_pr - (intstor_pr - self.intstor_pr_prevt) - r_pr_meas,
                )
            )

            r_pr_mss = (
                self.mss_frac
                * (1.0 - self.discfrac_pr)
                * max(
                    0.0,
                    p_atm - e_atm_pr - (intstor_pr - self.intstor_pr_prevt) - r_pr_meas,
                )
            )

            r_pr_up = self.discfrac_pr * max(
                0.0, p_atm - e_atm_pr - (intstor_pr - self.intstor_pr_prevt) - r_pr_meas
            )

            # update state
            self.intstor_pr_prevt = intstor_pr

        return {
            "int_pr": int_pr,
            "e_atm_pr": e_atm_pr,
            "intstor_pr": intstor_pr,
            "r_pr_meas": r_pr_meas,
            "r_pr_swds": r_pr_swds,
            "r_pr_mss": r_pr_mss,
            "r_pr_up": r_pr_up,
        }
