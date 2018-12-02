class Measure:
    """
    Creates an instance of Measure example (Grassed-swale) class with given states and properties

    Args:
        meas_area -- predefined measure area [m^2]
        runoff_to_stor_layer --- predefined selection at which measure layer runoff from other areas is stored (1 or 3), Inflow from other areas can only take place at interception level (1) or at the bottom storage level (3).
        * prev_intstor_meas --- interception storage on the measure at previous time step [mm]
        intstor_meas_t0 --- predefined interception storage on the measure at t=0 [mm]
        ev_evaporation --- predefined selection if evaporation from measure is possible (1) or not (0)
        num_stor_lvl --- predefined number of storage levels (1, 2 or 3)
        infil_cap_meas --- predefined infiltration capacity of measure [mm/d] (4800mm/d)
        top_storcap_meas --- predefined storage capacity in top layer of measure (76.2mm)
        bot_storcap_meas --- predefined storage capacity in bottom layer of measure (182.88mm)
        * prev_top_stor_meas --- top layer storage at the end of previous time step [mm]
        top_stor_meas_t0 --- top layer storage at t = 0 [mm] (0 mm)
        * prev_bot_stor_meas --- bottom layer storage at the end of previous time step [mm]
        bot_stor_meas_t0 --- bottom layer storage at t = 0 [mm] (0 mm)

        int_cap_meas --- predefined interception storage capacity of measure [mm] (20mm)
        ts_area_meas --- predefined area of top layer storage area of measure [m^2]
        et_transpiration --- predefined selection if evapotranspiration from measure is possible (1) or not (0)
        e_fac_meas --- predefined evaporation factor of measure [-]
        in_infiltration --- predefined selection if infiltration from measure is possible (1) or not (0)
        tinf_cap_meas --- predefined infiltration capacity of top layer of measure [mm/d] (480mm/d)

        bs_area_meas --- predefined area of bottom layer storage area of measure [m^2]
        btm_et_transpiration --- predefined selection if transpiration from bottom layer of measure is possible (1) or not (0)
        connection_to_gw --- predefined percolation (connection) from measure to groundwater is possible (1) or not (0)
        gwl_limit_meas --- predefined limitation of percolation from measure to groundwater if groundwater level is below measure bottom level (1=yes; 0=no)
        k_sat_uz --- saturation permeability of soil [mm/d] (this parameter will be put into the paramter matrix of static_base.ini which is linked with soil type)
        b_level_meas --- predefined bottom level of measure [m -SL] (0.6858)
        btm_discharge_type --- predefined definition of discharge type from bottom layer of measure (0 = flux limited, 1 = level difference over resistance)
        br_cap_meas --- predefined runoff capacity from bottom layer of measure [mm/d] (flux=15mm/d)
        bdl_meas --- predefined discharge level from bottom layer of measure [mm]
        bdr_meas --- predefined hydraulic resistance for level induced discharge from bottom layer of measure [d]

        surf_runoff_meas_ow --- predefined definition of surface runoff from measure storage 1 (interception level) to open water (0 = no, 1 = yes)
        ctrl_runoff_meas_ow --- predefined definition of controlled runoff from measure storage 3 (bottom level) to open water (0 = no, 1 = yes)
        overflow_meas_ow --- predefined definition of overflow from measure storage 3 (bottom level) to open water (0 = no, 1 = yes)
        surf_runoff_meas_uz --- predefined definition of surface runoff from measure storage 1 (interception level) to unsaturated zone (0 = no, 1 = yes)
        ctrl_runoff_meas_uz --- predefined definition of controlled runoff from measure to unsaturated zone (0 = no, 1 = yes)
        overflow_meas_uz --- predefined definition of overflow from measure to unsaturated zone (0 = no, 1 = yes)
        surf_runoff_meas_gw --- predefined definition of surface runoff from measure to groundwater (0 = no, 1 = yes)
        ctrl_runoff_meas_gw --- predefined definition of controlled runoff from measure to groundwater (0 = no, 1 = yes)
        overflow_meas_gw --- predefined definition of overflow from measure to groundwater (0 = no, 1 = yes)
        surf_runoff_meas_swds --- predefined definition of surface runoff from measure to storm water drainage system (0 = no, 1 = yes)
        ctrl_runoff_meas_swds --- predefined definition of controlled runoff from measure to storm water drainage system (0 = no, 1 = yes)
        overflow_meas_swds --- predefined definition of overflow from measure to storm water drainage system (0 = no, 1 = yes)
        surf_runoff_meas_mss --- predefined definition of surface runoff from measure to mixed sewer system (0 = no, 1 = yes)
        ctrl_runoff_meas_mss --- predefined definition of controlledrunoff from measure to mixed sewer system (0 = no, 1 = yes)
        overflow_meas_mss --- predefined definition of overflow from measure to mixed sewer system (0 = no, 1 = yes)
        surf_runoff_meas_out --- predefined definition of surface runoff from measure to outside water (0 = no, 1 = yes)
        ctrl_runoff_meas_out --- predefined definition of controlled runoff from measure to outside water (0 = no, 1 = yes)
        overflow_meas_out --- predefined definition of overflow from measure to outside water (0 = no, 1 = yes)
        # Several buttons are not applied yet in the current measure. They will be added at later stage (other measures). (for e.g Button_BQ22)
    Returns:
        A dictionary of output variables


    """
    def __init__(self, meas_area, runoff_to_stor_layer, intstor_meas_t0, ev_evaporation, num_stor_lvl, infil_cap_meas,
                top_storcap_meas, bot_storcap_meas, top_stor_meas_t0, bot_stor_meas_t0, int_cap_meas, ts_area_meas,
                et_transpiration, e_fac_meas, in_infiltration, tinf_cap_meas, bs_area_meas, btm_et_transpiration, connection_to_gw, gwl_limit_meas,
                k_sat_uz, b_level_meas, btm_discharge_type, br_cap_meas, bdl_meas, bdr_meas, surf_runoff_meas_ow, ctrl_runoff_meas_ow,
                overflow_meas_ow, surf_runoff_meas_uz, ctrl_runoff_meas_uz, overflow_meas_uz, surf_runoff_meas_gw, ctrl_runoff_meas_gw, overflow_meas_gw, surf_runoff_meas_swds,
                ctrl_runoff_meas_swds, overflow_meas_swds, surf_runoff_meas_mss, ctrl_runoff_meas_mss, overflow_meas_mss, surf_runoff_meas_out, ctrl_runoff_meas_out, overflow_meas_out):
        """
        Creates an instance of Measure class.
        """

        self.meas_area = meas_area
        self.runoff_to_stor_layer = runoff_to_stor_layer
        self.prev_intstor_meas = intstor_meas_t0
        self.ev_evaporation = ev_evaporation
        self.num_stor_lvl = num_stor_lvl
        self.infil_cap_meas = infil_cap_meas
        self.top_storcap_meas = top_storcap_meas
        self.bot_storcap_meas = bot_storcap_meas
        self.prev_top_stor_meas = top_stor_meas_t0
        self.prev_bot_stor_meas = bot_stor_meas_t0

        self.int_cap_meas = int_cap_meas
        self.ts_area_meas = ts_area_meas
        self.et_transpiration = et_transpiration
        self.e_fac_meas = e_fac_meas
        self.in_infiltration = in_infiltration
        self.tinf_cap_meas = tinf_cap_meas

        self.bs_area_meas = bs_area_meas
        self.btm_et_transpiration = btm_et_transpiration
        self.connection_to_gw = connection_to_gw
        self.gwl_limit_meas = gwl_limit_meas
        self.k_sat_uz = k_sat_uz
        self.b_level_meas = b_level_meas
        self.btm_discharge_type = btm_discharge_type
        self.br_cap_meas = br_cap_meas
        self.bdl_meas = bdl_meas
        self.bdr_meas = bdr_meas

        self.surf_runoff_meas_ow = surf_runoff_meas_ow
        self.ctrl_runoff_meas_ow = ctrl_runoff_meas_ow
        self.overflow_meas_ow = overflow_meas_ow
        self.surf_runoff_meas_uz = surf_runoff_meas_uz
        self.ctrl_runoff_meas_uz = ctrl_runoff_meas_uz
        self.overflow_meas_uz = overflow_meas_uz
        self.surf_runoff_meas_gw = surf_runoff_meas_gw
        self.ctrl_runoff_meas_gw = ctrl_runoff_meas_gw
        self.overflow_meas_gw = overflow_meas_gw
        self.surf_runoff_meas_swds = surf_runoff_meas_swds
        self.ctrl_runoff_meas_swds = ctrl_runoff_meas_swds
        self.overflow_meas_swds = overflow_meas_swds
        self.surf_runoff_meas_mss = surf_runoff_meas_mss
        self.ctrl_runoff_meas_mss = ctrl_runoff_meas_mss
        self.overflow_meas_mss = overflow_meas_mss
        self.surf_runoff_meas_out = surf_runoff_meas_out
        self.ctrl_runoff_meas_out = ctrl_runoff_meas_out
        self.overflow_meas_out = overflow_meas_out

    def sol(self, p_atm, e_pot_ow, r_pr_meas, r_cp_meas, r_op_meas, r_up_meas, pr_no_meas_area, cp_no_meas_area,
            op_no_meas_area, up_no_meas_area, gw_no_meas_area, prev_gwl_gw, delta_t,
            ):
            """
            sol function
            Args:
                _no_meas_area --- areas of the different land use elements where no measure is applied [m^2]
                p_atm --- rainfall during current time step [mm]
                e_pot_ow --- potential open water evaporation [mm]
                r_pr_meas --- runoff from paved roof to measure [mm]
                r_cp_meas --- runoff from closed paved to measure [mm]
                r_op_meas --- runoff from open paved to measure [mm]
                r_up_meas --- runoff from unpaved to measure [mm]
                pr_no_meas_area --- area of paved roof (without a measure) [m^2]
                cp_no_meas_area --- area of closed paved (without a measure) [m^2]
                op_no_meas_area --- area of open paved (without a measure) [m^2]
                up_no_meas_area --- area of unpaved (without a measure) [m^2]
                gw_no_meas_area --- area of groundwater (without a measure) [m^2]
                prev_gwl_gw --- groundwater level at previous time step [m -SL]
                delta_t --- time step size [d]

            returns:
                prec_meas --- direct rainfall on measure during the current time step [mm]
                sum_r_meas --- total runoff from paved roof, closed paved, open paved, unpaved to the measure during current time step [mm]
                int_meas --- interception on the measure after rainfall during current time step [mm]
                e_atm_meas --- evaporation form the storage layer1 (surface) during current time step [mm]
                int_down_meas --- downward flow from measure interception layer during current time step [mm]
                sr_meas --- surface runoff from measure during current time step [mm]
                intstor_meas --- interception storage on measure during current time step [mm]
                ts_ini_meas --- top layer storage at the beginning of current time step [mm]
                tt_atm_meas --- transpiration from top layer of measure at the current time step [mm]
                pt_meas --- percolation from top layer of measure at the current time step [mm]
                top_stor_meas --- top layer storage at the end of current time step [mm]
                bs_ini_meas --- bottom layer storage at the beginning of current time step [mm]
                tb_atm_meas --- transpiration from bottom layer of measure at the current time step [mm]
                pb_meas_gw --- percolation from bottom layer of measure to groundwater during current time step [mm]
                br_meas --- runoff from the bottom layer of the measure during current time step [mm]
                bot_stor_meas --- bottom storage at the end of the current time step [mm]
                bo_meas --- bottom storage overflow during current time step [mm]
                q_meas_ow --- Measure outflow to open water during current time step [mm]
                q_meas_uz --- Measure outflow to unsaturated zone during current time step [mm]
                q_meas_gw --- Measure outflow to groundwater during current time step [mm]
                q_meas_swds --- Measure outflow to storm water drainage system during current time step [mm]
                q_meas_mss --- Measure outflow to mixed sewer system during current time step [mm]
                q_meas_out --- Measure outflow to outside water during current time step [mm]
            """

            if self.meas_area == 0:
                prec_meas = sum_r_meas = int_meas = e_atm_meas = int_down_meas = sr_meas = intstor_meas = ts_ini_meas = \
                            tt_atm_meas = pt_meas = top_stor_meas = bs_ini_meas = tb_atm_meas = pb_meas_gw = br_meas = \
                            bot_stor_meas = bo_meas = q_meas_ow = q_meas_uz = q_meas_gw = q_meas_swds = q_meas_mss = \
                            q_meas_out = 0
            else:
                prec_meas = p_atm

                sum_r_meas = (r_pr_meas * pr_no_meas_area + r_cp_meas * cp_no_meas_area + r_op_meas * op_no_meas_area + r_up_meas * up_no_meas_area) / self.meas_area

                int_meas = self.prev_intstor_meas + prec_meas + (sum_r_meas if self.runoff_to_stor_layer == 1 else 0)

                e_atm_meas = self.ev_evaporation * min(int_meas, e_pot_ow)

                if self.num_stor_lvl > 1.5:  # needs update state here.
                    int_down_meas = max(0, min(int_meas - e_atm_meas, delta_t * self.infil_cap_meas,
                                        ((self.top_storcap_meas - self.prev_top_stor_meas) if self.num_stor_lvl > 2.5 else
                                         (self.bot_storcap_meas - self.prev_bot_stor_meas))))
                else:
                    int_down_meas = 0

                sr_meas = max(0, int_meas - e_atm_meas - int_down_meas - self.int_cap_meas)

                intstor_meas = max(0, int_meas - e_atm_meas - int_down_meas - sr_meas)

                if self.num_stor_lvl < 2.5:
                    ts_ini_meas = 0
                else:
                    ts_ini_meas = 0 if self.ts_area_meas == 0 else self.prev_top_stor_meas + int_down_meas * (self.meas_area / self.ts_area_meas)

                tt_atm_meas = 0 if self.num_stor_lvl < 2.5 else self.et_transpiration * min(ts_ini_meas, self.e_fac_meas * e_pot_ow)
                # removed the in__infiltration button
                pt_meas = 0 if self.num_stor_lvl < 2.5 else max(0, min(ts_ini_meas - tt_atm_meas, delta_t * self.tinf_cap_meas))

                top_stor_meas = min(self.top_storcap_meas, ts_ini_meas - tt_atm_meas - pt_meas)

                if self.num_stor_lvl < 1.5:
                    bs_ini_meas = 0
                else:
                    if self.bs_area_meas == 0:
                        bs_ini_meas = 0
                    else:
                        bs_ini_meas = self.prev_bot_stor_meas + \
                                      (0 if self.runoff_to_stor_layer == 1 else sum_r_meas) + \
                                      ((int_down_meas * (self.meas_area / self.bs_area_meas)) if self.num_stor_lvl < 2.5 else (pt_meas * (self.ts_area_meas / self.bs_area_meas)))

                if self.btm_et_transpiration < 0.5:
                    tb_atm_meas = 0
                else:
                    if self.num_stor_lvl < 2.5:
                        tb_atm_meas = self.et_transpiration * min(bs_ini_meas, self.e_fac_meas * e_pot_ow)
                    else:
                        tb_atm_meas = self.et_transpiration * min(bs_ini_meas, self.e_fac_meas * e_pot_ow - tt_atm_meas)

                if self.connection_to_gw < 0.5:
                    pb_meas_gw = 0
                else:
                    if self.gwl_limit_meas < 0.5:
                        pb_meas_gw = max(0, min(bs_ini_meas - tb_atm_meas, delta_t * self.k_sat_uz))
                    else:
                        if prev_gwl_gw < self.b_level_meas:
                            pb_meas_gw = 0
                        else:
                            pb_meas_gw = min(0 if self.bs_area_meas == 0 else 1000*(prev_gwl_gw - self.b_level_meas) * (gw_no_meas_area / self.bs_area_meas), max(0, min(bs_ini_meas - tb_atm_meas, delta_t * self.k_sat_uz)))

                if self.btm_discharge_type < 0.5:
                    br_meas = min(delta_t * self.br_cap_meas, bs_ini_meas - tb_atm_meas - pb_meas_gw)
                else:
                    if self.bdr_meas == 0:
                        br_meas = min(max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas), 0)
                    else:
                        br_meas = min(max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas), delta_t * max(0, (bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas)) / self.bdr_meas)

                bot_stor_meas = min(self.bot_storcap_meas, bs_ini_meas - tb_atm_meas - pb_meas_gw - br_meas)

                bo_meas = max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - br_meas - bot_stor_meas)

                q_meas_ow = self.surf_runoff_meas_ow * sr_meas + (0 if self.bs_area_meas == 0 else (self.ctrl_runoff_meas_ow * br_meas + self.overflow_meas_ow * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_uz = self.surf_runoff_meas_uz * sr_meas + (0 if self.bs_area_meas == 0 else (self.ctrl_runoff_meas_uz * br_meas + self.overflow_meas_uz * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_gw = self.surf_runoff_meas_gw * sr_meas + (0 if self.bs_area_meas == 0 else (pb_meas_gw + self.ctrl_runoff_meas_gw * br_meas + self.overflow_meas_gw * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_swds = self.surf_runoff_meas_swds * sr_meas + (0 if self.bs_area_meas == 0 else (self.ctrl_runoff_meas_swds * br_meas + self.overflow_meas_swds * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_mss = self.surf_runoff_meas_mss * sr_meas + (0 if self.bs_area_meas == 0 else (self.ctrl_runoff_meas_mss * br_meas + self.overflow_meas_mss * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_out = self.surf_runoff_meas_out * sr_meas + (0 if self.bs_area_meas == 0 else (self.ctrl_runoff_meas_out * br_meas + self.overflow_meas_out * bo_meas) * self.meas_area / self.bs_area_meas)

                # update state:
                # update interception storage
                self.prev_top_stor_meas = top_stor_meas
                self.prev_bot_stor_meas = bot_stor_meas
                self.prev_intstor_meas = intstor_meas

            return {"prec_meas": prec_meas, "sum_r_meas": sum_r_meas, "int_meas": int_meas, "e_atm_meas": e_atm_meas,
                    "int_down_meas": int_down_meas, "sr_meas": sr_meas, "intstor_meas": intstor_meas,
                    "ts_ini_meas": ts_ini_meas, "tt_atm_meas": tt_atm_meas, "pt_meas": pt_meas,
                    "top_stor_meas": top_stor_meas, "bs_ini_meas": bs_ini_meas, "tb_atm_meas": tb_atm_meas,
                    "pb_meas_gw": pb_meas_gw, "br_meas": br_meas, "bot_stor_meas": bot_stor_meas, "bo_meas": bo_meas,
                    "q_meas_ow": q_meas_ow, "q_meas_uz": q_meas_uz, "q_meas_gw": q_meas_gw,
                    "q_meas_swds": q_meas_swds, "q_meas_mss": q_meas_mss,"q_meas_out": q_meas_out}



