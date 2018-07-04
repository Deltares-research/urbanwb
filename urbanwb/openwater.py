class OpenWater:
    def __init__(self, ow_no_meas_area, ow_level, q_ow_out_cap=200):
        """
        creates an instance of open water class with given states and properties,
        iterates sol function at each time step.
        """

        # state
        # prev_owl --- open water level at previous time step [m-SL], i.e. initial open water level.
        self.prev_owl = ow_level

        # properties
        # ow_no_meas_area --- area of open water (without a measure) [m^2].
        # q_ow_out_cap --- predefined discharge capacity from open water to outside water [mm/d]
        # ow_level --- predefined target open water level [m-SL].
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

        # parameters
        # prec_ow --- Direct rainfall on open water during the current time step [mm].
        # e_atm_ow --- Evarporation from open water during current time step [mm]
        # sum_r_ow --- Total runoff (from unpaved area) to open water during current time step [mm]
        # sum_d_ow --- Drainage from groundwater to open water during current time step [mm]
        # sum_q_ow --- Total outflow from sewer systems to open water during current time step [mm]
        # sum_so_ow --- Total sewer overflow from sewer systems to open water during current time step [mm]
        # r_meas_ow --- Inflow from measure area (if applicable) during current time step [mm]
        # q_ow_out --- Discharge from open water to outside water during current time step [mm]

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
