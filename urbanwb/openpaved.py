#! /usr/bin/env python
# -*- coding: utf-8 -*-


class OpenPaved:
    """
    Creates an instance of OpenPaved class with given initial states and properties, iterates sol() function to compute
    fluxes and states at each time step.

    Args:
        intstor_op_t0 (float): initial interception storage on open paved (at t=0) [mm]
        op_no_meas_area (float): area of open paved without measure [m^2]
        op_meas_area (float): area of open paved with measure [m^2]
        op_meas_inflow_area (float): measure inflow area from open paved, i.e. runoff inflow area to measure from open \
        paved (>= area of open paved with measure and <= total area of open paved) [m^2]
        intstorcap_op (float): predefined interception storage capacity on open paved [mm]
        infilcap_op (float): predefined infiltration capacity on open paved [mm/d]
        swds_frac (float): part of urban paved area with storm water drainage system (SWDS) [-]
        discfrac_op (float): part of open paved that is disconnected from sewer system [-]
    """

    def __init__(
        self,
        intstor_op_t0,
        op_no_meas_area,
        op_meas_area,
        op_meas_inflow_area,
        intstorcap_op=1.6,
        infilcap_op=1.0,
        swds_frac=1.0,
        discfrac_op=0.0,
        **kwargs
    ):
        """
        Creates an instance of OpenPaved class
        """

        # state

        # self.intstor_op_prevt (float): interception storage on open paved at previous time step [mm]
        self.intstor_op_prevt = intstor_op_t0

        # properties

        self.op_no_meas_area = op_no_meas_area
        self.op_meas_area = op_meas_area
        self.op_meas_inflow_area = op_meas_inflow_area
        self.intstorcap_op = intstorcap_op
        self.infilcap_op = infilcap_op
        self.swds_frac = swds_frac

        # self.mss_frac (float): part of urban paved area with mixed sewer system (MSS) [-]
        self.mss_frac = 1.0 - self.swds_frac
        self.discfrac_op = discfrac_op

        # self.inflowfac_op (float): measure inflow factor of open paved
        self.inflowfac_op = self.inflowfac()

    def inflowfac(self):
        """
        Calculates measure inflow factor of open paved.

        Returns:
            (float): measure inflow factor of open paved

            * **inflowfac** -- measure inflow factor is calculated as (runoff inflow area to measure from open paved - \
            area of open paved with measure) / area of open paved without measure
        """
        if self.op_meas_inflow_area != 0.0:
            return (self.op_meas_inflow_area - self.op_meas_area) / self.op_no_meas_area
        else:
            0.0

    def sol(self, p_atm, e_pot_ow, delta_t):
        """
        Calculates states and fluxes on open paved during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]
            delta_t (float): length of time step [d]

        Returns:
            (dictionary): A dictionary of computed storage and fluxes during current time step:

            * **int_op** -- Interception storage on open paved after rainfall at the beginning of current time step [mm]
            * **e_atm_op** -- Evaporation from interception storage on open paved during current time step [mm]
            * **intstor_op** -- Remaining interception storage on open paved at the end of current time step [mm]
            * **p_op_gw** -- Percolation from interception storage on open paved to groundwater during current time step [mm]
            * **r_op_meas** -- Runoff from open paved to measure during current time step (not necessarily on open paved itself) [mm]
            * **r_op_swds** -- Runoff from open paved to storm water drainage system (SWDS) during current time step [mm]
            * **r_op_mss** -- Runoff from open paved to mixed sewer system (MSS) during current time step [mm]
            * **r_op_up** -- Runoff from open paved to unpaved during current time step [mm]

        """

        if self.op_no_meas_area == 0.0:
            int_op = (
                e_atm_op
            ) = intstor_op = p_op_gw = r_op_meas = r_op_swds = r_op_mss = r_op_up = 0.0

        else:
            int_op = min(self.intstorcap_op, max(0.0, p_atm + self.intstor_op_prevt))

            e_atm_op = min(e_pot_ow, int_op)

            intstor_op = int_op - e_atm_op

            p_op_gw = max(
                0.0,
                min(
                    p_atm - (self.intstorcap_op - self.intstor_op_prevt),
                    self.infilcap_op * delta_t,
                ),
            )

            r_op_meas = self.inflowfac_op * max(
                0.0, p_atm - e_atm_op - (intstor_op - self.intstor_op_prevt) - p_op_gw
            )

            r_op_swds = (
                self.swds_frac
                * (1.0 - self.discfrac_op)
                * max(
                    0.0,
                    p_atm
                    - e_atm_op
                    - (intstor_op - self.intstor_op_prevt)
                    - p_op_gw
                    - r_op_meas,
                )
            )

            r_op_mss = (
                self.mss_frac
                * (1.0 - self.discfrac_op)
                * max(
                    0.0,
                    p_atm
                    - e_atm_op
                    - (intstor_op - self.intstor_op_prevt)
                    - p_op_gw
                    - r_op_meas,
                )
            )

            r_op_up = self.discfrac_op * max(
                0.0,
                p_atm
                - e_atm_op
                - (intstor_op - self.intstor_op_prevt)
                - p_op_gw
                - r_op_meas,
            )

            # update state
            self.intstor_op_prevt = intstor_op

        return {
            "int_op": int_op,
            "e_atm_op": e_atm_op,
            "intstor_op": intstor_op,
            "p_op_gw": p_op_gw,
            "r_op_meas": r_op_meas,
            "r_op_swds": r_op_swds,
            "r_op_mss": r_op_mss,
            "r_op_up": r_op_up,
        }
