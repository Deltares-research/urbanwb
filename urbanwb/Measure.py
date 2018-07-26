class Measure:
    """
    Creates an instance of Measure example (Grassed-swale) class with given states and properties

    Args:
        meas_area -- predefined measure area [m^2]
        Button_BW17 --- predefined selection at which measure layer runoff from other areas is stored (1 or 3), Inflow from other areas can only take place at interception level (1) or at the bottom storage level (3).
        * prev_intstor_meas --- interception storage on the measure at previous time step [mm]
        intstor_meas_t0 --- predefined interception storage on the measure at t=0 [mm]
        Button_BQ19 --- predefined selection if evaporation from measure is possible (1) or not (0)
        Button_BQ18 --- predefined number of storage levels (1, 2 or 3)
        infil_cap_meas --- predefined infiltration capacity of measure [mm/d] (4800mm/d)
        top_storcap_meas --- predefined storage capacity in top layer of measure (76.2mm)
        bot_storcap_meas --- predefined storage capacity in bottom layer of measure (182.88mm)
        * prev_top_stor_meas --- top layer storage at the end of previous time step [mm]
        top_stor_meas_t0 --- top layer storage at t = 0 [mm] (0 mm)
        * prev_bot_stor_meas --- bottom layer storage at the end of previous time step [mm]
        bot_stor_meas_t0 --- bottom layer storage at t = 0 [mm] (0 mm)

        int_cap_meas --- predefined interception storage capacity of measure [mm] (20mm)
        ts_area_meas --- predefined area of top layer storage area of measure [m^2]
        Button_BQ20 --- predefined selection if transpiration from measure is possible (1) or not (0)
        e_fac_meas --- predefined evaporation factor of measure [-]
        tinf_cap_meas --- predefined infiltration capacity of top layer of measure [mm/d] (480mm/d)

        bs_area_meas --- predefined area of bottom layer storage area of measure [m^2]
        Button_CL21 --- predefined selection if transpiration from bottom layer of measure is possible (1) or not (0)
        Button_CL17 --- predefined connection from measure to groundwater (1 = yes. 0 = no)
        gwl_limit_meas --- predefined limitation of percolation from measure to groundwater if groundwater level is below measure bottom level (1=yes; 0=no)
        k_sat_uz --- saturation permeability of soil [mm/d]
        b_level_meas --- predefined bottom level of measure [m -SL] (0.6858)
        Button_CP14 --- predefined definition of discharge type from bottom layer of measure (0 = flux limited, 1 = level difference over resistance)
        br_cap_meas --- predefined runoff capacity from bottom layer of measure [mm/d] (flux=15mm/d)
        bdl_meas --- predefined discharge level from bottom layer of measure [mm]
        bdr_meas --- predefined hydraulic resistance for level induced discharge from bottom layer of measure [d]

        button_BW25 --- predefined definition of surface runoff from measure to open water (0 = no, 1 = yes)
        button_BW26 --- predefined definition of controlled runoff from measure to open water (0 = no, 1 = yes)
        button_BW27 --- predefined definition of overflow from measure to open water (0 = no, 1 = yes)
        button_BX25 --- predefined definition of surface runoff from measure to unsaturated zone (0 = no, 1 = yes)
        button_BX26 --- predefined definition of controlled runoff from measure to unsaturated zone (0 = no, 1 = yes)
        button_BX27 --- predefined definition of overflow from measure to unsaturated zone (0 = no, 1 = yes)
        button_BY25 --- predefined definition of surface runoff from measure to groundwater (0 = no, 1 = yes)
        button_BY26 --- predefined definition of controlled runoff from measure to groundwater (0 = no, 1 = yes)
        button_BY27 --- predefined definition of overflow from measure to groundwater (0 = no, 1 = yes)
        button_BZ25 --- predefined definition of surface runoff from measure to storm water drainage system (0 = no, 1 = yes)
        button_BZ26 --- predefined definition of controlled runoff from measure to storm water drainage system (0 = no, 1 = yes)
        button_BZ27 --- predefined definition of overflow from measure to storm water drainage system (0 = no, 1 = yes)
        button_CA25 --- predefined definition of surface runoff from measure to mixed sewer system (0 = no, 1 = yes)
        button_CA26 --- predefined definition of controlled runoff from measure to mixed sewer system (0 = no, 1 = yes)
        button_CA27 --- predefined definition of overflow from measure to mixed sewer system (0 = no, 1 = yes)
        button_CB25 --- predefined definition of surface runoff from measure to outside water (0 = no, 1 = yes)
        button_CB26 --- predefined definition of controlled runoff from measure to outside water (0 = no, 1 = yes)
        button_CB27 --- predefined definition of overflow from measure to outside water (0 = no, 1 = yes)

    Returns:
        A dictionary of output variables
    """
    def __init__(self, meas_area, Button_BW17, intstor_meas_t0, Button_BQ19, Button_BQ18, infil_cap_meas,
                top_storcap_meas, bot_storcap_meas, top_stor_meas_t0, bot_stor_meas_t0, int_cap_meas, ts_area_meas,
                Button_BQ20, e_fac_meas, tinf_cap_meas, bs_area_meas, Button_CL21, Button_CL17, gwl_limit_meas,
                k_sat_uz, b_level_meas, Button_CP14, br_cap_meas, bdl_meas, bdr_meas, Button_BW25, Button_BW26,
                Button_BW27, Button_BX25, Button_BX26, Button_BX27, Button_BY25, Button_BY26, Button_BY27, Button_BZ25,
                Button_BZ26, Button_BZ27, Button_CA25, Button_CA26, Button_CA27, Button_CB25, Button_CB26, Button_CB27):
        """
        Creates an instance of Measure class.
        """

        self.meas_area = meas_area
        self.Button_BW17 = Button_BW17
        self.prev_intstor_meas = intstor_meas_t0
        self.Button_BQ19 = Button_BQ19
        self.Button_BQ18 = Button_BQ18
        self.infil_cap_meas = infil_cap_meas
        self.top_storcap_meas = top_storcap_meas
        self.bot_storcap_meas = bot_storcap_meas
        self.prev_top_stor_meas = top_stor_meas_t0
        self.prev_bot_stor_meas = bot_stor_meas_t0

        self.int_cap_meas = int_cap_meas
        self.ts_area_meas = ts_area_meas
        self.Button_BQ20 = Button_BQ20
        self.e_fac_meas = e_fac_meas
        self.tinf_cap_meas = tinf_cap_meas

        self.bs_area_meas = bs_area_meas
        self.Button_CL21 = Button_CL21
        self.Button_CL17 = Button_CL17
        self.gwl_limit_meas = gwl_limit_meas
        self.k_sat_uz = k_sat_uz
        self.b_level_meas = b_level_meas
        self.Button_CP14 = Button_CP14
        self.br_cap_meas = br_cap_meas
        self.bdl_meas = bdl_meas
        self.bdr_meas = bdr_meas

        self.Button_BW25 = Button_BW25
        self.Button_BW26 = Button_BW26
        self.Button_BW27 = Button_BW27
        self.Button_BX25 = Button_BX25
        self.Button_BX26 = Button_BX26
        self.Button_BX27 = Button_BX27
        self.Button_BY25 = Button_BY25
        self.Button_BY26 = Button_BY26
        self.Button_BY27 = Button_BY27
        self.Button_BZ25 = Button_BZ25
        self.Button_BZ26 = Button_BZ26
        self.Button_BZ27 = Button_BZ27
        self.Button_CA25 = Button_CA25
        self.Button_CA26 = Button_CA26
        self.Button_CA27 = Button_CA27
        self.Button_CB25 = Button_CB25
        self.Button_CB26 = Button_CB26
        self.Button_CB27 = Button_CB27

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

                int_meas = self.prev_intstor_meas + prec_meas + (sum_r_meas if self.Button_BW17 == 1 else 0)

                e_atm_meas = self.Button_BQ19 * min(int_meas, e_pot_ow)

                if self.Button_BQ18 > 1.5:  # needs update state here.
                    int_down_meas = max(0, min(int_meas - e_atm_meas, delta_t * self.infil_cap_meas,
                                        ((self.top_storcap_meas - self.prev_top_stor_meas) if self.Button_BQ18 > 2.5 else
                                         (self.bot_storcap_meas - self.prev_bot_stor_meas))))
                else:
                    int_down_meas = 0

                sr_meas = max(0, int_meas - e_atm_meas - int_down_meas - self.int_cap_meas)

                intstor_meas = max(0, int_meas - e_atm_meas - int_down_meas - sr_meas)

                if self.Button_BQ18 < 2.5:
                    ts_ini_meas = 0
                else:
                    ts_ini_meas = 0 if self.ts_area_meas == 0 else self.prev_top_stor_meas + int_down_meas * (self.meas_area / self.ts_area_meas)

                tt_atm_meas = 0 if self.Button_BQ18 < 2.5 else self.Button_BQ20 * min(ts_ini_meas, self.e_fac_meas * e_pot_ow)

                pt_meas = 0 if self.Button_BQ18 < 2.5 else max(0, min(ts_ini_meas - tt_atm_meas, delta_t * self.tinf_cap_meas))

                top_stor_meas = min(self.top_storcap_meas, ts_ini_meas - tt_atm_meas - pt_meas)

                if self.Button_BQ18 < 1.5:
                    bs_ini_meas = 0
                else:
                    if self.bs_area_meas == 0:
                        bs_ini_meas = 0
                    else:
                        bs_ini_meas = self.prev_bot_stor_meas + \
                                      (0 if self.Button_BW17 == 1 else sum_r_meas) + \
                                      ((int_down_meas * (self.meas_area / self.bs_area_meas)) if self.Button_BQ18 < 2.5 else (pt_meas * (self.ts_area_meas / self.bs_area_meas)))

                if self.Button_CL21 < 0.5:
                    tb_atm_meas = 0
                else:
                    if self.Button_BQ18 < 2.5:
                        tb_atm_meas = self.Button_BQ20 * min(bs_ini_meas, self.e_fac_meas * e_pot_ow)
                    else:
                        tb_atm_meas = self.Button_BQ20 * min(bs_ini_meas, self.e_fac_meas * e_pot_ow - tt_atm_meas)

                if self.Button_CL17 < 0.5:
                    pb_meas_gw = 0
                else:
                    if self.gwl_limit_meas < 0.5:
                        pb_meas_gw = max(0, min(bs_ini_meas - tb_atm_meas, delta_t * self.k_sat_uz))
                    else:
                        if prev_gwl_gw < self.b_level_meas:
                            pb_meas_gw = 0
                        else:
                            pb_meas_gw = min(0 if self.bs_area_meas == 0 else 1000*(prev_gwl_gw - self.b_level_meas) * (gw_no_meas_area / self.bs_area_meas), max(0, min(bs_ini_meas - tb_atm_meas, delta_t * self.k_sat_uz)))

                if self.Button_CP14 < 0.5:
                    br_meas = min(delta_t * self.br_cap_meas, bs_ini_meas - tb_atm_meas - pb_meas_gw)
                else:
                    if self.bdr_meas == 0:
                        br_meas = min(max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas), 0)
                    else:
                        br_meas = min(max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas), delta_t * max(0, (bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas)) / self.bdr_meas)

                bot_stor_meas = min(self.bot_storcap_meas, bs_ini_meas - tb_atm_meas - pb_meas_gw - br_meas)

                bo_meas = max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - br_meas - bot_stor_meas)

                q_meas_ow = self.Button_BW25 * sr_meas + (0 if self.bs_area_meas == 0 else (self.Button_BW26 * br_meas + self.Button_BW27 * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_uz = self.Button_BX25 * sr_meas + (0 if self.bs_area_meas == 0 else (self.Button_BX26 * br_meas + self.Button_BX27 * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_gw = self.Button_BY25 * sr_meas + (0 if self.bs_area_meas == 0 else (pb_meas_gw + self.Button_BY26 * br_meas + self.Button_BY27 * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_swds = self.Button_BZ25 * sr_meas + (0 if self.bs_area_meas == 0 else (self.Button_BZ26 * br_meas + self.Button_BZ27 * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_mss = self.Button_CA25 * sr_meas + (0 if self.bs_area_meas == 0 else (self.Button_CA26 * br_meas + self.Button_CA27 * bo_meas) * self.meas_area / self.bs_area_meas)

                q_meas_out = self.Button_CB25 * sr_meas + (0 if self.bs_area_meas == 0 else (self.Button_CB26 * br_meas + self.Button_CB27 * bo_meas) * self.meas_area / self.bs_area_meas)

                # update state:

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





