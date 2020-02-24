#! /usr/bin/env python
# -*- coding: utf-8 -*-

from urbanwb.selector import et_selector, soil_selector
from urbanwb.gwlcalculator import gwlcalc


class UnsaturatedZone:
    """
    Creates an instance of UnsaturatedZone class with given initial states and properties, iterates sol() function to
    compute states and fluxes of unsaturated zone at each time step.

    Args:
        theta_uz_t0 (float): initial (volumetric) moisture content of soil in the root zone (at t=0) [mm]
        uz_no_meas_area (float): area of unsaturated zone without measure [m^2]
        uz_meas_area (float): area of unsaturated zone with measure [m^2]
        soiltype (int): soil type
        croptype (int): crop type
    """

    def __init__(
        self,
        theta_uz_t0,
        uz_no_meas_area,
        uz_meas_area,
        soiltype=2,
        croptype=1,
        **kwargs
    ):
        """
        Creates an instance of UnsaturatedZone class
        """

        # state

        # self.theta_uz_prevt (float): volumetric moisture content of soil in the root zone at previous time step [mm]
        self.theta_uz_prevt = theta_uz_t0

        # properties

        self.uz_no_meas_area = uz_no_meas_area
        self.uz_meas_area = uz_meas_area
        self.soiltype = soiltype
        self.croptype = croptype

        # self.et_prm (dataframe): a matrix of root zone - related parameters
        self.et_prm = et_selector(self.soiltype, self.croptype)

        # self.theta_h3l (float): equilibrium moisture content of soil in root zone, transpiration (E_pot ≤ 1 mm/d) reduction starts
        self.theta_h3l = self.et_prm["theta_h3l_mm"].values[0]

        # self.theta_h3h (float): equilibrium moisture content of soil in root zone, transpiration (E_pot ≥ 5 mm/d) reduction starts
        self.theta_h3h = self.et_prm["theta_h3h_mm"].values[0]

        # self.theta_h1 (float): equilibrium moisture content of soil in root zone, groundwater level at surface level, i.e. complete saturation
        self.theta_h1 = self.et_prm["theta_h1_mm"].values[0]

        # self.theta_h2 (float): equilibrium moisture content of soil in root zone, groundwater level at bottom root zone, i.e. field capacity
        self.theta_h2 = self.et_prm["theta_h2_mm"].values[0]

        # self.theta_h4 (float): equilibrium moisture content of soil in root zone, transpiration = 0, i.e. permernant wilting point
        self.theta_h4 = self.et_prm["theta_h4_mm"].values[0]

        # self.soil_prm (dataframe): soil parameter matrix dependent on soil type and crop type
        self.soil_prm = soil_selector(self.soiltype, self.croptype)

        # self.k_sat_uz (float): predefined saturated permeability of soil
        self.k_sat_uz = 10 * self.soil_prm[0]["k_sat"]

    def sol(self, i_up_uz, meas_uz, e_ref, tot_meas_area, gwl_prevt, delta_t=1 / 24):
        """
        Calculates states and fluxes in unsaturated zone during current time step.

        Args:
            i_up_uz (float): infiltration from interception storage on unpaved to unsaturated zone during current time step [mm]
            meas_uz (float): inflow from measure to unsaturated zone during current time step [mm]
            e_ref (float): reference crop evapotranspiration during current time step [mm]
            tot_meas_area (float): total area of measure [m^2]
            gwl_prevt (float): groundwater level at previous time step [m-SL]
            delta_t (float): length of time step [d]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of unsaturated zone during current time step:

            * **sum_i_uz** -- Infiltration from unpaved to unsaturated zone during current time step [mm]
            * **r_meas_uz** -- Inflow from measure (if applicable) to unsaturated zone during current time step [mm]
            * **theta_h3_uz** -- Moisture content of root zone at which transpiration reduction starts during current time step [mm]
            * **t_alpha_uz** -- Transpiration reduction factor during current time step [-]
            * **t_atm_uz** -- Transpiration from unsaturated zone during current time step [mm]
            * **gwl_up** -- First value in predefined lookup table above the groundwater level at the end of previous time step [m-SL]
            * **gwl_low** -- First value in predefined lookup table below the groundwater level at the end of previous time step [m-SL]
            * **theta_eq_uz** -- Equilibrium moisture content of root zone during current time step [mm]
            * **capris_max_uz** -- Maximum capillary rise in root zone during current time step [mm/d]
            * **p_uz_gw** -- Percolation from unsaturated zone to groundwater during current time step (positive: deep percolation, negative: capillary rise) [mm]
            * **theta_uz** -- Moisture content of root zone at the end of current time step [mm]
        """

        # parameters
        if self.uz_no_meas_area == 0.0:
            sum_i_uz = (
                r_meas_uz
            ) = (
                theta_h3_uz
            ) = (
                t_alpha_uz
            ) = (
                t_atm_uz
            ) = (
                gwl_up
            ) = gwl_low = theta_eq_uz = capris_max_uz = p_uz_gw = theta_uz = 0.0

        else:
            sum_i_uz = i_up_uz

            r_meas_uz = meas_uz * tot_meas_area / self.uz_no_meas_area

            if e_ref / (2.0 * delta_t) < 1.0:
                theta_h3_uz = self.theta_h3l
            elif e_ref / (2.0 * delta_t) > 5.0:
                theta_h3_uz = self.theta_h3h
            else:
                theta_h3_uz = self.theta_h3l + (e_ref / (2.0 * delta_t) - 1.0) / 4.0 * (
                    self.theta_h3h - self.theta_h3l
                )

            if self.theta_uz_prevt + sum_i_uz + r_meas_uz > self.theta_h1:
                t_alpha_uz = 0.0
            elif self.theta_uz_prevt + sum_i_uz + r_meas_uz > self.theta_h2:
                t_alpha_uz = 1.0 - (
                    (self.theta_uz_prevt + sum_i_uz + r_meas_uz) - self.theta_h2
                ) / (self.theta_h1 - self.theta_h2)
            elif self.theta_uz_prevt + sum_i_uz + r_meas_uz > theta_h3_uz:
                t_alpha_uz = 1.0
            elif self.theta_uz_prevt + sum_i_uz + r_meas_uz > self.theta_h4:
                t_alpha_uz = (
                    (self.theta_uz_prevt + sum_i_uz + r_meas_uz) - self.theta_h4
                ) / (theta_h3_uz - self.theta_h4)
            else:
                t_alpha_uz = 0.0

            t_atm_uz = e_ref * t_alpha_uz

            gwl_sol = gwlcalc(gwl_prevt)
            gwl_up = gwl_sol[0]
            gwl_low = gwl_sol[1]
            id1 = gwl_sol[2]
            id2 = gwl_sol[3]

            if gwl_prevt < 10.0:
                theta_eq_uz = self.soil_prm[id2]["moist_cont_eq_rz[mm]"] + (
                    gwl_low - gwl_prevt
                ) / (gwl_low - gwl_up) * (
                    self.soil_prm[id1]["moist_cont_eq_rz[mm]"]
                    - self.soil_prm[id2]["moist_cont_eq_rz[mm]"]
                )
                capris_max_uz = self.soil_prm[id2]["capris_max[mm/d]"] + (
                    gwl_low - gwl_prevt
                ) / (gwl_low - gwl_up) * (
                    self.soil_prm[id1]["capris_max[mm/d]"]
                    - self.soil_prm[id2]["capris_max[mm/d]"]
                )
            else:
                theta_eq_uz = self.soil_prm[29]["moist_cont_eq_rz[mm]"]
                capris_max_uz = self.soil_prm[29]["capris_max[mm/d]"]

            if self.theta_uz_prevt + sum_i_uz + r_meas_uz - t_atm_uz > theta_eq_uz:
                p_uz_gw = min(
                    self.theta_uz_prevt + sum_i_uz + r_meas_uz - t_atm_uz - theta_eq_uz,
                    delta_t * self.k_sat_uz,
                )
            else:
                p_uz_gw = -1.0 * min(
                    theta_eq_uz
                    - (self.theta_uz_prevt + sum_i_uz + r_meas_uz - t_atm_uz),
                    delta_t * capris_max_uz,
                )

            theta_uz = self.theta_uz_prevt + sum_i_uz + r_meas_uz - t_atm_uz - p_uz_gw

            # update state
            self.theta_uz_prevt = theta_uz

        return {
            "sum_i_uz": sum_i_uz,
            "r_meas_uz": r_meas_uz,
            "theta_h3_uz": theta_h3_uz,
            "t_alpha_uz": t_alpha_uz,
            "t_atm_uz": t_atm_uz,
            "gwl_up": gwl_up,
            "gwl_low": gwl_low,
            "theta_eq_uz": theta_eq_uz,
            "capris_max_uz": capris_max_uz,
            "p_uz_gw": p_uz_gw,
            "theta_uz": theta_uz,
        }
