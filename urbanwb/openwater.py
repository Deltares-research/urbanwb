#! /usr/bin/env python
# -*- coding: utf-8 -*-


class OpenWater:
    """
    Creates an instance of OpenWater class with given initial states and properties, iterates sol() function to compute
    states and fluxes of open water at each time step.

    Args:
        ow_no_meas_area (float): area of open water without measure [m^2]
        q_ow_out_cap (float): discharge capacity from open water (internal) to outside water (external) [mm/d]
        ow_level (float): predefined target open water level, also the initial open water level (at t=0) [m-SL]
    """

    def __init__(self, ow_no_meas_area, q_ow_out_cap, ow_level, **kwargs):
        """
        Creates an instance of OpenWater class.
        """

        # state

        # self.owl_prevt (float): open water level at previous time step [m-SL]
        self.owl_prevt = ow_level

        # properties
        self.ow_no_meas_area = ow_no_meas_area
        self.q_ow_out_cap = q_ow_out_cap
        self.ow_level = ow_level

    def sol(
        self,
        p_atm,
        e_pot_ow,
        r_up_ow,
        d_gw_ow,
        q_swds_ow,
        q_mss_ow,
        so_swds_ow,
        so_mss_ow,
        meas_ow,
        up_no_meas_area,
        gw_no_meas_area,
        swds_no_meas_area,
        mss_no_meas_area,
        tot_meas_area,
        tot_area,
        delta_t=1 / 24,
    ):
        """
        Calculates states and fluxes on open water during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]
            r_up_ow (float): runoff from unpaved to open water during current time step [mm]
            d_gw_ow (float): drainage from groundwater to open water during current time step [mm]
            q_swds_ow (float): Outflow from storm water drainage system (SWDS) to open water during current time step [mm]
            q_mss_ow (float): Outflow from combined sewer system (MSS) to open water during current time step [mm]
            so_swds_ow (float): Sewer overflow of storm water drainage system (SWDS) during current time step [mm]
            so_mss_ow (float): Sewer overflow of combined sewer system (MSS) during current time step [mm]
            meas_ow (float): inflow from measure (if applicable) to open water during current time step [mm]
            up_no_meas_area (float): area of unpaved without measure [m^2]
            gw_no_meas_area (float): area of groundwater without measure [m^2]
            swds_no_meas_area (float): area of storm water drainage system (SWDS) without measure [m^2]
            mss_no_meas_area (float): area of combined sewer system (MSS) without measure [m^2]
            tot_meas_area (float): total area of measure [m^2]
            tot_area (float): total area of study area [m^2]
            delta_t (float): length of time step [d]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of open water during current time step:

            * **prec_ow** -- Direct rainfall on open water during current time step [mm]
            * **e_atm_ow** -- Evaporation from open water during current time step [mm]
            * **sum_r_ow** -- Total runoff from unpaved to open water during current time step [mm]
            * **sum_d_ow** -- Drainage from groundwater to open water during current time step [mm]
            * **sum_q_ow** -- Total outflow from sewer systems to open water during current time step [mm]
            * **sum_so_ow** -- Total sewer overflow from sewer systems to open water during current time step [mm]
            * **r_meas_ow** -- Inflow from measure (if applicable) to open water during current time step [mm]
            * **q_ow_out** -- Discharge from open water to outside water during current time step [mm]
        """

        if self.ow_no_meas_area == 0.0:
            prec_ow = e_atm_ow = sum_r_ow = sum_d_ow = sum_q_ow = sum_so_ow = (
                r_meas_ow
            ) = q_ow_out = 0.0

            # if no area of open water without measure is defined, open water level is then a fixed drainage level.
            owl = self.ow_level

        else:
            prec_ow = p_atm

            e_atm_ow = e_pot_ow

            sum_r_ow = r_up_ow * up_no_meas_area / self.ow_no_meas_area

            sum_d_ow = d_gw_ow * gw_no_meas_area / self.ow_no_meas_area

            sum_q_ow = (
                q_swds_ow * swds_no_meas_area + q_mss_ow * mss_no_meas_area
            ) / self.ow_no_meas_area

            sum_so_ow = (
                so_swds_ow * swds_no_meas_area + so_mss_ow * mss_no_meas_area
            ) / self.ow_no_meas_area

            r_meas_ow = meas_ow * tot_meas_area / self.ow_no_meas_area

            q_ow_out = min(
                delta_t * self.q_ow_out_cap * (tot_area / self.ow_no_meas_area),
                1000.0 * (self.ow_level - self.owl_prevt)
                + prec_ow
                - e_atm_ow
                + sum_r_ow
                + sum_d_ow
                + sum_q_ow
                + sum_so_ow
                + r_meas_ow,
            )

            owl = (
                self.owl_prevt
                - (
                    prec_ow
                    - e_atm_ow
                    + sum_r_ow
                    + sum_d_ow
                    + sum_q_ow
                    + sum_so_ow
                    + r_meas_ow
                    - q_ow_out
                )
                / 1000.0
            )

            # # runoff over the entire area (currently excluding Q to WWTP)
            # # r_ow_entire = (max(- (owl - self.owl_prevt), 0) * 1000.0 + max(q_ow_out, 0.0)) * (self.ow_no_meas_area / tot_area)
            # # without groundwater drainage to surface water
            # r_ow_entire1 = (sum_r_ow + sum_q_ow + sum_so_ow + r_meas_ow) * (self.ow_no_meas_area / tot_area)
            # # with groundwater drainage to surface water
            # r_ow_entire2 = (sum_r_ow + sum_d_ow + sum_q_ow + sum_so_ow + r_meas_ow) * (self.ow_no_meas_area / tot_area)
            # r_ow_entire3 = (max(- (owl - self.owl_prevt), 0) * 1000.0 + max(q_ow_out, 0.0)) * (self.ow_no_meas_area / tot_area)
            # r_ow_entire4 = (- (owl - self.owl_prevt) * 1000.0 + max(q_ow_out, 0.0)) * (self.ow_no_meas_area / tot_area)

            # update state
            self.owl_prevt = owl

        return {
            "prec_ow": prec_ow,
            "e_atm_ow": e_atm_ow,
            "sum_r_ow": sum_r_ow,
            "sum_d_ow": sum_d_ow,
            "sum_q_ow": sum_q_ow,
            "sum_so_ow": sum_so_ow,
            "r_meas_ow": r_meas_ow,
            "q_ow_out": q_ow_out,
            "owl": owl,
            # "r_ow_entire1": r_ow_entire1,
            # "r_ow_entire2": r_ow_entire2,
            # "r_ow_entire3": r_ow_entire3,
            # "r_ow_entire4": r_ow_entire4,
        }
