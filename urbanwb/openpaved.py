class OpenPaved:
    """
    creates an instance of open paved class with given states and properties, iterates sol function at each time step.
    """

    def __init__(
        self,
        init_intstor_op_t0,
        op_no_meas_area,
        op_meas_area,
        op_meas_inflow_area,
        intstorcap_op=1.6,
        stormfrac_op=1.0,
        discfrac_op=0.0,
        infilcap_op=1.0,
    ):

        # state
        # init_intstor_op --- initial interception storage on open paved [mm].
        self.init_intstor_op = init_intstor_op_t0

        # properties
        # op_no_meas_area --- open paved area (without a measure) [m^2].
        # op_meas_area --- open paved area (with a measure) [m^2].
        # op_meas_inflow_area --- measure inflow area (>= measure area and <= total area) [m^2].
        # intstorcap_op --- predefined storage capacity on open paved [mm].
        # stormfrac_op --- part of urban area with storm water drainage system [-].
        # mxdfrac--- part of urban area with mixed sewer system [-].
        # discfrac_op --- part of open paved area that is disconnected [-].
        # infilcap_op --- predefined infiltration capacity on open paved area [mm/d].

        self.op_no_meas_area = op_no_meas_area
        self.op_meas_area = op_meas_area
        self.op_meas_inflow_area = op_meas_inflow_area
        self.intstorcap = intstorcap_op
        self.stormfrac = stormfrac_op
        self.mxdfrac = 1 - self.stormfrac
        self.discfrac = discfrac_op
        self.infilcap = infilcap_op

    def inflowfac(self):
        return (self.op_meas_inflow_area - self.op_meas_area) / self.op_no_meas_area

    def sol(self, p_atm, e_pot_ow, delta_t):

        # parameters
        # int_op --- Interception on open paved after rainfall during current time step [mm].
        # e_atm_op --- Evaporation from interception storage on open paved during current time step [mm].
        # intstor_op --- Remaining interception storage on open paved at the end of the current time step [mm].
        # p_op_gw --- Percolation of interception storage on open paved to groundwater during current time step [mm].
        # r_op_meas --- Runoff from open paved to an area with a drainage measure
        # (not necessarily on the open paved area itself) [mm].
        # r_op_swds --- Runoff from open paved to the storm water drainage system [mm].
        # r_op_mss --- Runoff from open paved to the mixed sewer system [mm].
        # r_op_up --- Runoff from open paved to unpaved area [mm].

        if self.op_no_meas_area == 0:
            int_op = (
                e_atm_op
            ) = intstor_op = p_op_gw = r_op_meas = r_op_swds = r_op_mss = r_op_up = 0

        else:
            int_op = min(self.intstorcap, max(0, p_atm + self.init_intstor_op))

            e_atm_op = min(e_pot_ow, int_op)

            intstor_op = int_op - e_atm_op

            p_op_gw = max(
                0,
                min(
                    p_atm - (self.intstorcap - self.init_intstor_op),
                    self.infilcap * delta_t,
                ),
            )  # infiltration capacity (mm/d) * time step size (hr to d)

            r_op_meas = self.inflowfac() * max(
                0, p_atm - e_atm_op - (intstor_op - self.init_intstor_op) - p_op_gw
            )

            r_op_swds = (
                self.stormfrac
                * (1 - self.discfrac)
                * max(
                    0,
                    p_atm
                    - e_atm_op
                    - (intstor_op - self.init_intstor_op)
                    - p_op_gw
                    - r_op_meas,
                )
            )

            r_op_mss = (
                self.mxdfrac
                * (1 - self.discfrac)
                * max(
                    0,
                    p_atm
                    - e_atm_op
                    - (intstor_op - self.init_intstor_op)
                    - p_op_gw
                    - r_op_meas,
                )
            )

            r_op_up = self.discfrac * max(
                0,
                p_atm
                - e_atm_op
                - (intstor_op - self.init_intstor_op)
                - p_op_gw
                - r_op_meas,
            )

            # update state
            self.init_intstor_op = intstor_op

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
