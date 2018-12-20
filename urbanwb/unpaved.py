#! /usr/bin/env python
# -*- coding: utf-8 -*-

from urbanwb.selector import soil_selector


class Unpaved:
    """
    creates an instance of Unpaved class with given initial states and properties, iterates sol() function to compute
    fluxes and states at each time step.

    Args:
        fin_intstor_up_t0: initial final remaining interception storage on unpaved (at t=0) [mm]
        up_no_meas_area (float): area of unpaved without measure [m^2]
        up_meas_area (float): area of unpaved with measure [m^2]
        up_meas_inflow_area (float): measure inflow area from unpaved, i.e. runoff inflow area to measure from unpaved \
        (>= area of unpaved with measure and <= total area of unpaved) [m^2]
        intstorcap_up (float): predefined interception storage capacity on unpaved [mm]
        infilcap_up (float): predefined infiltration capacity on unpaved [mm/d]
        soiltype (int): Soil type
        croptype (int): Crop type
    """

    def __init__(
        self,
        fin_intstor_up_t0,
        up_no_meas_area,
        up_meas_area,
        up_meas_inflow_area,
        intstorcap_up=20,
        infilcap_up=48,
        soiltype=2,
        croptype=1,
        **kwargs
    ):
        """
        Creates an instance of Unpaved class.
        """

        # state

        # self.fin_intstor_up_prevt (float): final remaining interception storage on unpaved at previous time step [mm]
        self.fin_intstor_up_prevt = fin_intstor_up_t0

        # properties

        self.up_no_meas_area = up_no_meas_area
        self.up_meas_area = up_meas_area
        self.up_meas_inflow_area = up_meas_inflow_area
        self.intstorcap_up = intstorcap_up
        self.infilcap_up = infilcap_up
        self.soiltype = soiltype
        self.croptype = croptype

        # self.soil_prm (dataframe): soil parameter matrix dependent on soil type and crop type
        self.soil_prm = soil_selector(self.soiltype, self.croptype)

        # self.mois_uz_max: maximum moisture content in root zone [mm]
        self.mois_uz_max = self.soil_prm[0]["moist_cont_eq_rz[mm]"]

        # self.k_sat_uz: predefined saturated permeability of unsaturated zone [mm/d]
        self.k_sat_uz = 10 * self.soil_prm[0]["k_sat"]

        # self.inflowfac_up (float): measure inflow factor of unpaved
        self.inflowfac_up = self.inflowfac()

    def inflowfac(self):
        """
        Calculates measure inflow factor of unpaved.

        Returns:
            (float): measure inflow factor of unpaved

            * **inflowfac** -- measure inflow factor is calculated as (runoff inflow area to measure from unpaved - \
            area of unpaved with measure) / area of unpaved without measure
        """

        if self.up_no_meas_area != 0.0:
            return (self.up_no_meas_area - self.up_meas_area) / self.up_no_meas_area
        else:
            return 0.0

    def sol(
        self,
        p_atm,
        e_pot_ow,
        r_pr_up,
        r_cp_up,
        r_op_up,
        mois_uz_prevt,
        pr_no_meas_area,
        cp_no_meas_area,
        op_no_meas_area,
        ow_no_meas_area,
        delta_t=1 / 24,
    ):
        """
        Calculates states and fluxes  on unpaved during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]
            r_pr_up (float): runoff from paved roof to unpaved during current time step [mm]
            r_cp_up (float): runoff from closed paved to unpaved during current time step [mm]
            r_op_up (float): runoff from open paved to unpaved during current time step[mm]
            mois_uz_prevt (float): moisture content in root zone at previous time step [mm]
            pr_no_meas_area (float): area of paved roof without measure [m^2]
            cp_no_meas_area (float): area of closed paved without measure [m^2]
            op_no_meas_area (float): area of open paved without measure [m^2]
            ow_no_meas_area (float): area of open water without measure [m^2]
            delta_t (float): length of time step [d]

        Returns:
            (dictionary): A dictionary of computed storage and fluxes during current time step:

            * **sum_r_up** -- Runoff from all paved areas to unpaved during current time step [mm]
            * **init_intstor_up** -- Initial interception storage on unpaved after rainfall at the beginning of current time step [mm]
            * **actl_infilcap_up** -- Actual infiltration capacity on unpaved during current time step [mm]
            * **timefac_up** -- Time factor [-]. Part of current time step that interception storage on unpaved is \
            available for infiltration and evaporation during current time step
            * **e_atm_up** -- Evaporation from interception storage on unpaved during current time step [mm]
            * **i_up_uz** -- Infiltration from interception storage on unpaved to unsaturated zone during current time step [mm]
            * **fin_intstor_up** -- Final remaining interception storage on unpaved at the end of current time step [mm]
            * **r_up_meas** -- Runoff from unpaved to measure during current time step (not necessarily on unpaved itself) [mm]
            * **r_up_ow** -- Runoff from unpaved to open water during current time step [mm]
        """

        if self.up_no_meas_area == 0.0:
            sum_r_up = (
                init_intstor_up
            ) = (
                actl_infilcap_up
            ) = timefac_up = e_atm_up = i_up_uz = fin_intstor_up = r_up_meas = r_up_ow = 0.0

        else:
            sum_r_up = (
                r_pr_up * pr_no_meas_area
                + r_cp_up * cp_no_meas_area
                + r_op_up * op_no_meas_area
            ) / self.up_no_meas_area

            init_intstor_up = self.fin_intstor_up_prevt + p_atm + sum_r_up

            actl_infilcap_up = min(
                delta_t * self.infilcap_up,
                self.mois_uz_max
                - mois_uz_prevt
                + min(self.mois_uz_max - mois_uz_prevt, delta_t * self.k_sat_uz),
            )

            if e_pot_ow + actl_infilcap_up <= 0.0:
                timefac_up = 0.0
            else:
                timefac_up = min(1.0, init_intstor_up / (e_pot_ow + actl_infilcap_up))

            e_atm_up = timefac_up * e_pot_ow

            i_up_uz = timefac_up * actl_infilcap_up

            if ow_no_meas_area == 0.0:
                fin_intstor_up = max(
                    0.0,
                    min(
                        self.intstorcap_up
                        + (
                            self.up_no_meas_area
                            - (self.up_meas_inflow_area - self.up_meas_area)
                        )
                        / self.up_no_meas_area
                        * (init_intstor_up - e_atm_up - i_up_uz - self.intstorcap_up),
                        init_intstor_up - e_atm_up - i_up_uz,
                    ),
                )

            else:
                fin_intstor_up = max(
                    0.0, min(self.intstorcap_up, init_intstor_up - e_atm_up - i_up_uz)
                )

            r_up_meas = self.inflowfac_up * max(
                0.0, init_intstor_up - e_atm_up - i_up_uz - self.intstorcap_up
            )

            if ow_no_meas_area == 0.0:
                r_up_ow = 0.0
            else:
                r_up_ow = max(
                    0.0,
                    init_intstor_up - e_atm_up - i_up_uz - self.intstorcap_up - r_up_meas,
                )

            # update state
            self.fin_intstor_up_prevt = fin_intstor_up

        return {
            "sum_r_up": sum_r_up,
            "init_intstor_up": init_intstor_up,
            "actl_infilcap_up": actl_infilcap_up,
            "timefac_up": timefac_up,
            "e_atm_up": e_atm_up,
            "i_up_uz": i_up_uz,
            "fin_intstor_up": fin_intstor_up,
            "r_up_meas": r_up_meas,
            "r_up_ow": r_up_ow,
        }
