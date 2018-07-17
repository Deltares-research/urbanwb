class OpenWater:
    """
    Creates an instance of OpenWater class with given stats and properties, iterates sol() function at each time step

    Args:
        self.ow_no_meas_area (float): area of open water (without a measure) [m^2].
        self.q_ow_out_cap (float): predefined discharge capacity from open water to outside water [mm/d]
        self.ow_level (float): predefined target open water level [m-SL], also the initial open water level at t=0
    """

    def __init__(self, ow_no_meas_area, ow_level, q_ow_out_cap=200):
        """
        Creates an instance of OpenWater class.
        """

        # state
        # self.prev_owl (float): open water level at previous time step [m-SL], i.e. initial open water level.
        self.prev_owl = ow_level

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
        total_area,
        delta_t=1 / 24,
    ):
        """
        Calculates storage and fluxes during current time step

        Args:
            p_atm (float): precipitation during current time step [mm]
            e_pot_ow (float): potential evaporation during current time step [mm]
            r_up_ow (float): runoff from unpaved to open water during current time step [mm]
            d_gw_ow (float): drainage from groundwater to open water [mm]
            q_swds_ow (float): Outflow from storm water drainage system to open water during the current time step [mm]
            q_mss_ow (float): Outflow from mixed sewer system to open water during the current time step [mm]
            so_swds_ow (float): Sewer overflow of storm water drainage system during the current time step [mm]
            so_mss_ow (float): Sewer overflow of mixed sewer system during the current time step [mm]
            meas_ow (float): measure inflow to open water during current time step [mm]
            up_no_meas_area (float): area of unpaved (without a measure) [m^2]
            gw_no_meas_area (float): area of groundwater (without a measure) [m^2]
            swds_no_meas_area (float): area of storm water drainage system (without a measure) [m^2]
            mss_no_meas_area (float): area of mixed sewer system (without a measure) [m^2]
            tot_meas_area (float): total measure area [m^2]
            total_area (float): total area [m^2]
            delta_t (float): time step size [d]

        Returns:
            (dictionary): A dictionary of storage and fluxes during current time step:


            * **prec_ow** -- Direct rainfall on open water during the current time step [mm]
            * **e_atm_ow** -- Evarporation from open water during current time step [mm]
            * **sum_r_ow** -- Total runoff (from unpaved area) to open water during current time step [mm]
            * **sum_d_ow** -- Drainage from groundwater to open water during current time step [mm]
            * **sum_q_ow** -- Total outflow from sewer systems to open water during current time step [mm]
            * **sum_so_ow** -- Total sewer overflow from sewer systems to open water during current time step [mm]
            * **r_meas_ow** -- Inflow from measure area (if applicable) during current time step [mm]
            * **q_ow_out** -- Discharge from open water to outside water during current time step [mm]
         """
        # parameters
        if self.ow_no_meas_area == 0:
            prec_ow = (
                e_atm_ow
            ) = sum_r_ow = sum_d_ow = sum_q_ow = sum_so_ow = r_meas_ow = q_ow_out = 0

            # if no open water area is defined, then owl means fixed drainage level for all time steps.
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

            q_ow_out = (self.ow_no_meas_area / total_area) * min(
                delta_t * self.q_ow_out_cap * (total_area / self.ow_no_meas_area),
                1000 * (self.ow_level - self.prev_owl)
                + prec_ow
                - e_atm_ow
                + sum_r_ow
                + sum_d_ow
                + sum_q_ow
                + sum_so_ow
                + r_meas_ow,
            )

            owl = (
                self.prev_owl
                - (
                    prec_ow
                    - e_atm_ow
                    + sum_r_ow
                    + sum_d_ow
                    + sum_q_ow
                    + sum_so_ow
                    + r_meas_ow
                    - (total_area / self.ow_no_meas_area) * q_ow_out
                )
                / 1000
            )

            # update state
            self.prev_owl = owl

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
        }
