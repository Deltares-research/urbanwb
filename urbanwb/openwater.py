class OpenWater:
    """Creates an instance of OpenWater class with given initial states and properties, iterates sol() function to compute
    states and fluxes of open water at each time step.

    Args:
        ow_no_meas_area (float): area of open water without measure [m^2]
        ow_level (float): predefined target open water level, also the initial open water level (at t=0) [m-SL]
        q_ow_out_cap (float): discharge capacity from open water (internal) to outside water (external) [mm/d].
            Mutually exclusive with q_ow_out_qh.
        q_ow_out_qh (list of [h, Q] pairs): Q(h) relation defining discharge capacity [mm/d] as a function of open
            water level [m-SL]. Q=0 at water levels below the first defined point. Linear interpolation between
            points, linear extrapolation beyond the last point based on the last segment slope.
            Mutually exclusive with q_ow_out_cap.
        q_ow_in_cap (float): inlet capacity from outside water to open water [mm/d]. Default is inf (unlimited).

    """

    def __init__(
        self,
        ow_no_meas_area,
        ow_level,
        q_ow_out_cap=None,
        q_ow_out_qh=None,
        q_ow_in_cap=float("inf"),
        **kwargs,
    ):
        """Creates an instance of OpenWater class."""
        if q_ow_out_cap is not None and q_ow_out_qh is not None:
            raise ValueError("Cannot specify both q_ow_out_cap and q_ow_out_qh.")
        if q_ow_out_cap is None and q_ow_out_qh is None:
            raise ValueError("Must specify either q_ow_out_cap or q_ow_out_qh.")
        if q_ow_out_qh is not None and q_ow_in_cap != 0:
            raise ValueError(
                "q_ow_in_cap must be 0 when using q_ow_out_qh (Q(h) relation defines the full discharge behavior)."
            )

        # state
        # self.owl_prevt (float): open water level at previous time step [m-SL]
        self.owl_prevt = ow_level

        # properties
        self.ow_no_meas_area = ow_no_meas_area
        self.q_ow_out_cap = q_ow_out_cap
        self.q_ow_in_cap = q_ow_in_cap
        self.ow_level = ow_level

        if q_ow_out_qh is not None:
            sorted_qh = sorted(q_ow_out_qh, key=lambda p: p[0])
            self._qh_h = [p[0] for p in sorted_qh]
            self._qh_q = [p[1] for p in sorted_qh]
        else:
            self._qh_h = None
            self._qh_q = None

    def _qh_discharge(self, owl):
        """Evaluate discharge capacity from Q(h) relation at a given water level.

        Args:
            owl (float): open water level [m-SL]

        Returns:
            float: discharge capacity [mm/d]

        """
        h = self._qh_h
        q = self._qh_q

        # At or below the lowest water in the table (highest m-SL): Q = 0
        if owl >= h[-1]:
            return 0.0

        # Above the highest water in the table (lowest m-SL): extrapolate from first segment
        if owl <= h[0]:
            if len(h) < 2:
                return q[0]
            slope = (q[1] - q[0]) / (h[1] - h[0])
            return q[0] + slope * (owl - h[0])

        # Linear interpolation
        for i in range(len(h) - 1):
            if h[i] <= owl <= h[i + 1]:
                t = (owl - h[i]) / (h[i + 1] - h[i])
                return q[i] + t * (q[i + 1] - q[i])

        return 0.0

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
        """Calculates states and fluxes on open water during current time step.

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

            if self._qh_h is not None:
                discharge_cap = self._qh_discharge(self.owl_prevt)
            else:
                discharge_cap = self.q_ow_out_cap

            q_ow_out = min(
                delta_t * discharge_cap * (tot_area / self.ow_no_meas_area),
                1000.0 * (self.ow_level - self.owl_prevt)
                + prec_ow
                - e_atm_ow
                + sum_r_ow
                + sum_d_ow
                + sum_q_ow
                + sum_so_ow
                + r_meas_ow,
            )

            # Limit water inlet from outside water (negative q_ow_out)
            q_ow_out = max(
                q_ow_out,
                -delta_t * self.q_ow_in_cap * (tot_area / self.ow_no_meas_area),
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
