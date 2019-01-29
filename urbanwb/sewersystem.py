#! /usr/bin/env python
# -*- coding: utf-8 -*-


class SewerSystem:
    """
    Creates an instance of SewerSystem class with given initial states and properties, iterates sol() function to
    compute states and fluxes of sewer system at each time step.

    Args:
        swds_no_meas_area (float): area of storm water drainage system (SWDS) without measure [m^2]
        mss_no_meas_area (float): area of combined sewer system (MSS) without measure [m^2]
        stor_swds_t0 (float): initial storage in storm water drainage system (SWDS) (at t=0) [mm]
        so_swds_t0 (float): initial sewer overflow from storm water drainage system (SWDS) (at t=0) [mm]
        stor_mss_t0 (float): initial storage in combined sewer system (MSS) (at t=0) [mm]
        so_mss_t0 (float): initial sewer overflow from combined sewer system (MSS) (at t=0) [mm]
        q_swds_ow_cap (float): discharge capacity of storm water drainage system (SWDS) to open water [mm/timestep]
        q_mss_out_cap (float): discharge capacity of combined sewer system (MSS) to waste water treatment plant (WWTP) [mm/timestep]
        q_mss_ow_cap (float): discharge capacity of combined sewer system (MSS) to open water [mm/timestep]
        stor_swds_cap (float): predefined storage capacity of storm water drainage system (SWDS) [mm]
        stor_mss_cap (float): predefined storage capacity of combined sewer system (MSS) [mm]
    """

    def __init__(
        self,
        swds_no_meas_area,
        mss_no_meas_area,
        stor_swds_t0,
        so_swds_t0,
        stor_mss_t0,
        so_mss_t0,
        q_swds_ow_cap,
        q_mss_out_cap,
        q_mss_ow_cap,
        storcap_swds=2.0,
        storcap_mss=9.0,
        **kwargs
    ):
        """
        Creates an instance of SewerSystem class.
        """
        # state
        self.stor_swds_prevt = stor_swds_t0
        self.so_swds_prevt = so_swds_t0
        self.stor_mss_prevt = stor_mss_t0
        self.so_mss_prevt = so_mss_t0

        # properties
        self.swds_no_meas_area = swds_no_meas_area
        self.mss_no_meas_area = mss_no_meas_area
        self.q_swds_ow_cap = q_swds_ow_cap
        self.q_mss_out_cap = q_mss_out_cap
        self.q_mss_ow_cap = q_mss_ow_cap
        self.storcap_swds = storcap_swds
        self.storcap_mss = storcap_mss

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
        Calculates states and fluxes of sewer system during current time step.

        Args:
            pr_no_meas_area (float): area of paved roof without measure [m^2]
            cp_no_meas_area (float): area of closed paved without measure [m^2]
            op_no_meas_area (float): area of open paved without measure [m^2]
            r_pr_swds (float): runoff from paved roof to storm water drainage system during current time step [mm]
            r_cp_swds (float): runoff from closed paved to storm water drainage system during current time step [mm]
            r_op_swds (float): runoff from open paved to storm water drainage system during current time step [mm]
            r_pr_mss (float): runoff from paved roof to combined sewer system during current time step [mm]
            r_cp_mss (float): runoff from closed paved to combined sewer system during current time step [mm]
            r_op_mss (float): runoff from open paved to combined sewer system during current time step [mm]
            meas_swds (float): inflow from measure (if applicable) to storm water drainage system during current time step [mm]
            meas_mss (float): inflow from measure (if applicable) to combined sewer system during current time step [mm]
            ow_no_meas_area (float): area of open water without measure [m^2]
            tot_meas_area (float): total area of measure [m^2]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of sewer system during current time step:

            * **sum_r_swds** -- Sum of runoff from paved area to storm water drainage system during current time step [mm]
            * **r_meas_swds** -- Inflow from measure (if applicable) to storm water drainage system during current time step [mm]
            * **sum_r_mss** -- Sum of runoff from pave area to combined sewer system during current time step [mm]
            * **r_meas_mss** -- Inflow from measure (if applicable) to combined sewer system during current time step [mm]
            * **q_swds_ow** -- Outflow from storm water drainage system to open water during current time step [mm]
            * **q_mss_out** -- Discharge from combined sewer system to Waste Water Treatment Plant (WWTP) during current time step [mm]
            * **q_mss_ow** -- Outflow from combined sewer system to open water during current time step [mm]
            * **so_swds** -- Sewer overflow from storm water drainage system during current time step [mm]
            * **so_mss** -- Sewer overflow from combined sewer system during current time step [mm]
            * **stor_swds** -- Storage in storm water drainage system at the end of current time step [mm]
            * **stor_mss** -- Storage in combined sewer system at the end of current time step [mm]
        """

        if self.swds_no_meas_area == 0.0:
            sum_r_swds = r_meas_swds = q_swds_ow = so_swds = stor_swds = 0.0

        else:
            sum_r_swds = (
                pr_no_meas_area * r_pr_swds
                + cp_no_meas_area * r_cp_swds
                + op_no_meas_area * r_op_swds
            ) / self.swds_no_meas_area

            r_meas_swds = meas_swds * tot_meas_area / self.swds_no_meas_area

            if ow_no_meas_area == 0.0:
                q_swds_ow = min(
                    self.stor_swds_prevt + sum_r_swds + r_meas_swds + self.so_swds_prevt,
                    self.q_swds_ow_cap,
                )

                so_swds = max(
                    0.0,
                    self.stor_swds_prevt
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - self.storcap_swds
                    + self.so_swds_prevt,
                )

                stor_swds = max(
                    0.0,
                    self.stor_swds_prevt
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - (so_swds - self.so_swds_prevt),
                )

            else:
                q_swds_ow = min(
                    self.stor_swds_prevt + sum_r_swds + r_meas_swds + 0.0,
                    self.q_swds_ow_cap,
                )

                so_swds = max(
                    0.0,
                    self.stor_swds_prevt
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - self.storcap_swds
                    + 0.0,
                )

                stor_swds = max(
                    0.0,
                    self.stor_swds_prevt
                    + sum_r_swds
                    + r_meas_swds
                    - q_swds_ow
                    - so_swds,
                )

            # update state
            self.stor_swds_prevt = stor_swds

            self.so_swds_prevt = so_swds

        if self.mss_no_meas_area == 0.0:

            sum_r_mss = r_meas_mss = q_mss_out = q_mss_ow = so_mss = stor_mss = 0.0

        else:
            sum_r_mss = (
                pr_no_meas_area * r_pr_mss
                + cp_no_meas_area * r_cp_mss
                + op_no_meas_area * r_op_mss
            ) / self.mss_no_meas_area

            r_meas_mss = meas_mss * tot_meas_area / self.mss_no_meas_area

            if ow_no_meas_area == 0.0:
                q_mss_out = min(
                    self.stor_mss_prevt + sum_r_mss + r_meas_mss + self.so_mss_prevt,
                    self.q_mss_out_cap,
                )

                q_mss_ow = max(
                    0.0,
                    min(
                        self.stor_mss_prevt
                        + sum_r_mss
                        + r_meas_mss
                        - q_mss_out
                        + self.so_mss_prevt,
                        self.q_mss_ow_cap - self.q_mss_out_cap,
                    ),
                )

                so_mss = max(
                    0.0,
                    self.stor_mss_prevt
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - self.storcap_mss
                    + self.so_mss_prevt,
                )

                stor_mss = max(
                    0.0,
                    self.stor_mss_prevt
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - (so_mss - self.so_mss_prevt),
                )

            else:
                q_mss_out = min(
                    self.stor_mss_prevt + sum_r_mss + r_meas_mss + 0.0, self.q_mss_out_cap
                )

                q_mss_ow = max(
                    0.0,
                    min(
                        self.stor_mss_prevt + sum_r_mss + r_meas_mss - q_mss_out + 0.0,
                        self.q_mss_ow_cap - self.q_mss_out_cap,
                    ),
                )

                so_mss = max(
                    0.0,
                    self.stor_mss_prevt
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - self.storcap_mss
                    + 0.0,
                )

                stor_mss = max(
                    0.0,
                    self.stor_mss_prevt
                    + sum_r_mss
                    + r_meas_mss
                    - q_mss_out
                    - q_mss_ow
                    - so_mss,
                )

            # update state
            self.stor_mss_prevt = stor_mss

            self.so_mss_prevt = so_mss
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
