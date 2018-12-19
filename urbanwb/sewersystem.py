class SewerSystem:
    """
    creates an instance of SewerSystem class with given initial states and properties,
    iterates sol() function at each time step.

    Args:
        self.swds_no_meas_area (float): area of storm water drainage system (without a measure) [m^2]
        self.mss_no_meas_area (float): area of mixed sewer system (without a measure) [m^2]
        self.prev_stor_swds (float): storage in the storm water drainage system at the end of the previous time step [mm]
        self.prev_so_swds (float): overflow of storm water drainage system during the previous time step [mm]
        self.prev_stor_mss (float): storage in the mixed sewer system at the end of the previous time step [mm]
        self.prev_so_mss (float): overflow of mixed sewer system during the previous time step [mm]
        self.q_swds_ow_cap (float): predefined discharge capacity of storm water drainage system [mm/hr]
        self.q_mss_out_cap (float): predefined discharge capacity of mixed sewer system to WWTP [mm/hr]
        self.q_mss_ow_cap (float): predefined discharge capacity of mixed sewer system to open water [mm/hr]
        self.stor_swds_cap (float): predefined storage capacity of storm water drainage system [mm]
        self.stor_mss_cap (float): predefined storage capacity of mixed sewer system [mm]
    """

    def __init__(
        self,
        swds_no_meas_area,
        mss_no_meas_area,
        prev_stor_swds_t0,
        prev_so_swds_t0,
        prev_stor_mss_t0,
        prev_so_mss_t0,
        q_swds_ow_cap=55.1,
        q_mss_out_cap=26.3,
        q_mss_ow_cap=48.1,
        stor_swds_cap=2,
        stor_mss_cap=9,
        **kwargs
    ):
        """
        Creates an instance of SewerSystem class.
        """
        # state
        self.prev_stor_swds = prev_stor_swds_t0
        self.prev_so_swds = prev_so_swds_t0
        self.prev_stor_mss = prev_stor_mss_t0
        self.prev_so_mss = prev_so_mss_t0

        # properties
        # Note the relationship between q_swds_ow_cap, stor_swds_cap, cp_intstor_cap, rainfall intensity.
        self.swds_no_meas_area = swds_no_meas_area
        self.mss_no_meas_area = mss_no_meas_area
        self.q_swds_ow_cap = q_swds_ow_cap
        self.q_mss_out_cap = q_mss_out_cap
        self.q_mss_ow_cap = q_mss_ow_cap
        self.stor_swds_cap = stor_swds_cap
        self.stor_mss_cap = stor_mss_cap

    def sol(
        self,
        pr_no_meas_area,
        cp_no_meas_area,
        op_no_meas_area,
        r_pr_swds,
        r_cp_swds,
        r_op_swds,
        r_pr_mss,
        r_cp_mss,
        r_op_mss,
        meas_swds,
        meas_mss,
        ow_no_meas_area,
        tot_meas_area,
    ):
        """
        Calculates storage and fluxes during current time step.

        Args:
            pr_no_meas_area (float): area of paved roof (without a measure) [m^2]
            cp_no_meas_area (float): area of closed paved (without a measure) [m^2]
            op_no_meas_area (float): area of open paved (without a measure) [m^2]
            r_pr_swds (float): runoff from paved roof to storm water drainage system [mm]
            r_cp_swds (float): runoff from closed paved to storm water drainage system [mm]
            r_op_swds (float): runoff from open paved to storm water drainage system [mm]
            r_pr_mss (float): runoff from paved roof to mixed sewer system [mm]
            r_cp_mss (float): runoff from closed paved to mixed sewer system [mm]
            r_op_mss (float): runoff from open paved to mixed sewer system [mm]
            meas_swds (float): measure inflow to storm water drainage system [mm]
            meas_mss (float): measure inflow to mixed sewer system [mm]
            ow_no_meas_area (float): area of open water (without a measure) [m^2]
            tot_meas_area (float): total measure area [m^2]

        Returns:
            (dictionary): A dictionary of storage and fluxes during current time step:

            * **sum_r_swds** -- Total runoff to storm water drainage system during the current time step [mm]
            * **r_meas_swds** -- Inflow from measure area (if applicable) during current time step [mm]
            * **sum_r_mss** -- Total runoff to mixed sewer system during the current time step [mm]
            * **r_meas_mss** -- Inflow from measure area (if applicable) during current time step [mm]
            * **q_swds_ow** -- Outflow from storm water drainage system to open water [mm]
            * **q_mss_out** -- Discharge from mixed sewer system to Waste Water Treatment Plant (WWTP) during the current time step [mm]
            * **q_mss_ow** -- Outflow from mixed sewer system to open water during the current time step [mm]
            * **so_swds** -- Overflow of storm water drainage system during the current time step [mm]
            * **so_mss** -- Overflow of mixed sewer system during the current time step [mm]
            * **stor_swds** -- Storage in the storm water drainage system at the end of the current time step [mm]
            * **stor_mss** -- Storage in the mixed sewer system at the end of the current time step [mm]
        """

        # parameters
        if self.swds_no_meas_area == 0:

            sum_r_swds = r_meas_swds = q_swds_ow = so_swds = stor_swds = 0

        else:

            sum_r_swds = (
                pr_no_meas_area * r_pr_swds
                + cp_no_meas_area * r_cp_swds
                + op_no_meas_area * r_op_swds
            ) / self.swds_no_meas_area
            r_meas_swds = meas_swds * tot_meas_area / self.swds_no_meas_area

            if ow_no_meas_area == 0:
                q_swds_ow = min(
                    self.prev_stor_swds + sum_r_swds + r_meas_swds + self.prev_so_swds,
                    self.q_swds_ow_cap,
                )

                so_swds = max(
                    0,
                    self.prev_stor_swds
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - self.stor_swds_cap
                    + self.prev_so_swds,
                )

                stor_swds = max(
                    0,
                    self.prev_stor_swds
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - (so_swds - self.prev_so_swds),
                )

            else:
                q_swds_ow = min(
                    self.prev_stor_swds + sum_r_swds + r_meas_swds + 0,
                    self.q_swds_ow_cap,
                )

                so_swds = max(
                    0,
                    self.prev_stor_swds
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - self.stor_swds_cap
                    + 0,
                )

                stor_swds = max(
                    0,
                    self.prev_stor_swds
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - so_swds,
                )

            # update state
            self.prev_stor_swds = stor_swds
            self.prev_so_swds = so_swds

        if self.mss_no_meas_area == 0:

            sum_r_mss = r_meas_mss = q_mss_out = q_mss_ow = so_mss = stor_mss = 0

        else:
            sum_r_mss = (
                pr_no_meas_area * r_pr_mss
                + cp_no_meas_area * r_cp_mss
                + op_no_meas_area * r_op_mss
            ) / self.mss_no_meas_area
            r_meas_mss = meas_mss * tot_meas_area / self.mss_no_meas_area

            if ow_no_meas_area == 0:
                q_mss_out = min(
                    self.prev_stor_mss + sum_r_mss + r_meas_mss + self.prev_so_mss,
                    self.q_mss_out_cap,
                )

                q_mss_ow = max(
                    0,
                    min(
                        self.prev_stor_mss
                        + sum_r_mss
                        + r_meas_mss
                        - q_mss_out
                        + self.prev_so_mss,
                        self.q_mss_ow_cap - self.q_mss_out_cap,
                    ),
                )

                so_mss = max(
                    0,
                    self.prev_stor_mss
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - self.stor_mss_cap
                    + self.prev_so_mss,
                )

                stor_mss = max(
                    0,
                    self.prev_stor_mss
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - (so_mss - self.prev_so_mss),
                )

            else:
                q_mss_out = min(
                    self.prev_stor_mss + sum_r_mss + r_meas_mss + 0, self.q_mss_out_cap
                )

                q_mss_ow = max(
                    0,
                    min(
                        self.prev_stor_mss + sum_r_mss + r_meas_mss - q_mss_out + 0,
                        self.q_mss_ow_cap - self.q_mss_out_cap,
                    ),
                )

                so_mss = max(
                    0,
                    self.prev_stor_mss
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - self.stor_mss_cap
                    + 0,
                )

                stor_mss = max(
                    0,
                    self.prev_stor_mss
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - so_mss,
                )

            # update state
            self.prev_stor_mss = stor_mss
            self.prev_so_mss = so_mss
        return {
            "sum_r_swds": sum_r_swds,
            "r_meas_swds": r_meas_swds,
            "sum_r_mss": sum_r_mss,
            "r_meas_mss": r_meas_mss,
            "q_swds_ow": q_swds_ow,
            "q_mss_out": q_mss_out,
            "q_mss_ow": q_mss_ow,
            "so_swds_ow": so_swds,
            "so_mss_ow": so_mss,
            "stor_swds": stor_swds,
            "stor_mss": stor_mss,
        }
