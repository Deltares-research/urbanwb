class Measure:
    """
    Creates an instance of Measure(Grassed-swale) class with given states and properties

    Args:
        self.

    Returns:

    """
    def __init__(self, measure_area, intstor_meas_t0, Button_BW17, Button_BQ18, Button_BQ19, Button_CL21, infil_cap_meas, top_storcap_meas, bot_storcap_meas, int_cap_meas, ts_area_meas, e_fac_meas, tinf_cap_meas, top_stor_meas, br_cap_meas
                 ):
        # meas_area -- predefined measure area [m^2]
        # intstor_meas_t0 --- ..... at initial t=0
        # Button_BW17 --- predefined selection at which measure layer runoff from other areas is stored (1 or 3), Inflow from other areas can only take place at interception level (1) or at the bottom storage level (3).
        # Button_BQ19 --- predefined selection if evaporation from measure is possible (1) or not (0)
        # top_storcap_meas --- predefined storage capacity in top layer of measure
        # Bot_storcap_meas --- predefined storage capacity in bottom layer of measure
        # int_cap_meas --- predefined interception storage capacity of measure
        # infil_cap_meas --- predefined infiltration capacity of measure
        # e_fac_meas --- predefined evaporation factor of measure
        # Button_CL21 --- predefined selection if transpiration from bottom layer of measure is possible(1) or not (0)
        # ts_area_meas --- ts_area_meas


        self.Button_BW17 = Button_BW17
        self.Button_BQ19 = Button_BQ19
        self.Button_BQ18 = Button_BQ18
        self.Button_CL21 = Button_CL21
        self.meas_area = measure_area
        self.prev_intstor_meas = intstor_meas_t0
        self.infil_cap_meas = infil_cap_meas
        self.top_storcap_meas = top_storcap_meas
        self.bot_storcap_meas = bot_storcap_meas
        self.int_cap_meas = int_cap_meas
        self.ts_area_meas = ts_area_meas
        self.e_fac_meas = e_fac_meas
        self.tinf_cap_meas = tinf_cap_meas
        self.br_cap_meas = br_cap_meas


    def sol(self, p_atm, e_pot_ow, r_pr_meas, r_cp_meas, r_op_meas, r_up_meas, pr_no_meas_area, cp_no_meas_area, op_no_meas_area, up_no_meas_area, gw_no_meas_area, delta_t, prev_gwl_gw
            ):
        # prec_meas --- direct rainfall on measure during the current time step [mm]
        # sum_r_meas --- total runoff from paved roof, closed paved, open paved, unpaved to the measure during current time step [mm]
        # int_meas --- interception on the measure after rainfall during current time step [mm]
        # e_atm_meas --- evaporation form the storage layer1 (surface) during current time step [mm]
        # int_down_meas --- downward flow from measure interception layer during current time step [mm]
        # sr_meas --- surface runoff from measure during current time step [mm]
        # intstor_meas --- interception storage on measure during current time step [mm]
        # ts_ini_meas --- top layer storage at the beginning of current time step [mm]
        # tt_atm_meas --- transpiration from top layer of measure at the current time step [mm]
        # pt_meas --- percolation from top layer of measure at the current time step [mm]
        # top_stor_meas --- top layer storage at the end of current time step [mm]
        # bs_ini_meas --- bottom layer storage at the beginning of current time step [mm]
        # tb_atm_meas --- transpiration from bottom layer of measure at the current time step [mm]
        # pb_meas_gw --- percolation from bottom layer of measure to groundwater during current time step [mm]
        # br_meas --- runoff from the bottom layer of the measure during current time step [mm]
        # bot_stor_meas --- bottom storage at the end of the current time step [mm]
        # bo_meas --- bottom storage overflow during current time step [mm]
        # q_meas_ow --- Measure outflow to open water during current time step [mm]
        # q_meas_uz --- Measure outflow to unsaturated zone during current time step [mm]
        # q_meas_gw --- Measure outflow to groundwater during current time step [mm]
        # q_meas_swds --- Measure outflow to storm water drainage system during current time step [mm]
        # q_meas_mss --- Measure outflow to mixed sewer system during current time step [mm]
        # q_meas_out --- Measure outflow to outside water during current time step [mm]

        if self.meas_area == 0:
            prec_meas = sum_r_meas = int_meas = e_atm_meas = int_down_meas = sr_meas = intstor_meas = ts_ini_meas \
                    = tt_atm_meas = 0

        else:

            prec_meas = p_atm

            sum_r_meas = (r_pr_meas * pr_no_meas_area + r_cp_meas * cp_no_meas_area + r_op_meas * op_no_meas_area + r_up_meas * up_no_meas_area) / self.meas_area

            int_meas = self.prev_intstor_meas + prec_meas + ( sum_r_meas if self.Button_BW17 == 1 else 0)

            e_atm_meas = self.Button_BQ19 * min(int_meas, e_pot_ow)

            if self.Button_BQ18 > 1.5:  # needs update state here.
                int_down_meas = max(0, min(int_meas - e_atm_meas, delta_t * self.infil_cap_meas,
                                   ((self.top_storcap_meas - self.prev_top_stor_meas) if self.Button_BQ18 > 2.5 else (self.bot_storcap_meas - self.prev_bot_stor_meas))))
            else:
                int_down_meas = 0

            sr_meas = max(0, int_meas - e_atm_meas - int_down_meas - self.int_cap_meas)

            intstor_meas = max(0, int_meas - e_atm_meas - int_down_meas - sr_meas)
            # I have already test to this part. To be continued.
            if self.Button_BQ18 < 2.5:
                ts_ini_meas = 0
            else:
                ts_ini_meas = 0 if self.ts_area_meas == 0 else self.prev_top_stor_meas + int_down_meas * ( self.meas_area / self.ts_area_meas)

            tt_atm_meas = 0 if self.Button_BQ18 < 2.5 else self.ButtonBQ20 * min(ts_ini_meas, self.e_fac_meas * e_pot_ow)

            pt_meas = 0 if self.Button_BQ18 < 2.5 else max(0, min(ts_ini_meas - tt_atm_meas, delta_t * self.tinf_cap_meas))

            top_stor_meas = min(self.top_storcap_meas, ts_ini_meas - tt_atm_meas - pt_meas)

            if self.Button_BQ18 < 1.5:
                bs_ini_meas = 0
            else:
                if self.bs_area_meas == 0:
                    bs_ini_meas = 0
                else:
                    bs_ini_meas = self.prev_bot_stor_meas + 0 if self.Button_BW17 == 1 else (sum_r_meas + (int_down_meas * self.meas_area / self.ts_area_meas) if self.Button_BQ18 < 2.5 else pt_meas * (self.ts_area_meas / self.bs_area_meas))

            if self.Button_CL21 < 0.5:

                tb_atm_meas = 0

            else:
                if self.BQ18 < 2.5:
                    tb_atm_meas = self.Button_BQ20 * min(bs_ini_meas, self.e_fac_meas * e_pot_ow)

                else:
                    tb_atm_meas = self.Button_BQ20 * min(self.e_fac_meas * e_pot_ow - tt_atm_meas, bs_ini_meas)

            if self.Button_CL17 < 0.5:
                pb_meas_gw = 0
            else:
                if self.gwl_limit_meas < 0.5:
                    pb_meas_gw = max(0, min(bs_ini_meas - tb_atm_meas), delta_t * self.k_sat_uz)

                else:
                    if self.prev_gwl_gw < self.B_level_meas:
                        pb_meas_gw = 0
                    else:
                        pb_meas_gw = min(0 if self.bs_area_meas ==0 else 1000*(prev_gwl_gw - self.B_level_meas) * (gw_no_meas_area / self.bs_area_meas ), max(0, min(bs_ini_meas - tb_atm_meas, delta_t * self.k_sat_uz)))

            if self.Button_CP14 < 0.5:
                br_meas = min(delta_t * self.br_cap_meas, bs_ini_meas - tb_atm_meas - pb_meas_gw)
            else:
                if self.resistance == 0:
                    br_meas = min(max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas), 0)  # something wrong here
                else:
                    br_meas = min(max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas), delta_t * max(0, (bs_ini_meas - tb_atm_meas - pb_meas_gw - self.bdl_meas) / self.bdr_meas))

            bot_stor_meas = min(self.bot_storcap_meas, bs_ini_meas - tb_atm_meas - pb_meas_gw - br_meas)

            bo_meas = max(0, bs_ini_meas - tb_atm_meas - pb_meas_gw - br_meas - bot_stor_meas)

            q_meas_ow = self.Button_BW25 * sr_meas + (0 if self.bs_area_meas ==0 else (self.Button_BW26 * br_meas + self.Button_BW27 * bo_meas) * self.meas_area / self.bs_area_meas)

            q_meas_uz = self.Button_BX25 * sr_meas + (0 if self.bs_area_meas ==0 else (self.Button_BX26 * br_meas + self.Button_BX27 * bo_meas) * self.meas_area / self.bs_area_meas)

            q_meas_gw = self.Button_BY25 * sr_meas + (0 if self.bs_area_meas ==0 else (pb_meas_gw + self.Button_BY26 * br_meas + self.Button_BY27 * bo_meas) * self.meas_area / self.bs_area_meas)

            q_meas_swds = self.Button_BZ25 * sr_meas + (0 if self.bs_area_meas ==0 else (self.Button_BZ26 * br_meas + self.Button_BZ27 * bo_meas) * self.meas_area / self.bs_area_meas)

            q_meas_mss = self.Button_CA25 * sr_meas + (0 if self.bs_area_meas ==0 else (self.Button_CA26 * br_meas + self.Button_CA27 * bo_meas) * self.meas_area / self.bs_area_meas)

            q_meas_out = self.button_CB25 * sr_meas + (0 if self.bs_area_meas ==0 else (self.Button_CB26 * br_meas + self.Button_CB27 * bo_meas) * self.meas_area / self.bs_area_meas)

            # update state:
            self.prev_intstor_meas = intstor_meas

            return {"prec_meas": prec_meas, "sum_r_meas":sum_r_meas, "int_meas": int_meas, "e_atm_meas": e_atm_meas, "int_down_meas": int_down_meas,
                    "sr_meas": sr_meas, "ts_ini_meas": ts_ini_meas, "tt_atm_meas": tt_atm_meas, "pt_meas": pt_meas, "top_stor_meas": top_stor_meas,
                    "bs_ini_meas": bs_ini_meas, "tb_atm_meas": tb_atm_meas, "pb_meas_gw": pb_meas_gw, "br_meas": br_meas, "bot_stor_meas": bot_stor_meas,
                    "bo_meas": bo_meas, "q_meas_ow": q_meas_ow, "q_meas_uz": q_meas_uz, "q_meas_gw": q_meas_gw, "q_meas_swds": q_meas_swds, "q_meas_mss": q_meas_mss,
                    "q_meas_out": q_meas_out}


