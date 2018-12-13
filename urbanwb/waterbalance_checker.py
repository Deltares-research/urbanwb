class WaterBalanceChecker:  # think about make separate waterbalance checker for basics and measure.
    """
    This part works as a checker of the water balance. It checks both the water balance of the entire model and
    the water balance of the measure. Since Urbanwb is strictly conserved in water quantity.
    """
    def __init__(self, tot_area, pr_no_meas_area, cp_no_meas_area, op_no_meas_area, up_no_meas_area, ow_no_meas_area,
                 uz_no_meas_area, gw_no_meas_area, swds_no_meas_area, mss_no_meas_area, meas_area, meas_top_area, meas_bot_area, meas_inflow_area, inflowareaIsoparea=True):

        self.tot_area = tot_area
        self.pr_no_meas_area = pr_no_meas_area
        self.cp_no_meas_area = cp_no_meas_area
        self.op_no_meas_area = op_no_meas_area
        self.up_no_meas_area = up_no_meas_area
        self.ow_no_meas_area = ow_no_meas_area
        self.uz_no_meas_area = uz_no_meas_area
        self.gw_no_meas_area = gw_no_meas_area
        self.swds_no_meas_area = swds_no_meas_area
        self.mss_no_meas_area = mss_no_meas_area

        self.meas_area = meas_area
        self.meas_top_area = meas_top_area
        self.meas_bot_area = meas_bot_area
        self.op_meas_inflow_area = meas_inflow_area
        self.inflowareaIsoparea = inflowareaIsoparea

    def sol(self, P_atm, e_atm_pr, e_atm_cp, e_atm_op, e_atm_up, e_atm_ow, t_atm_uz, e_atm_meas, tt_atm_meas, tb_atm_meas,
            s_gw_out, d_gw_ow, q_swds_ow, q_mss_ow, sum_so_ow, q_mss_out, q_ow_out, q_meas_out, intstor_pr, intstor_pr_prevt,
            intstor_cp, intstor_cp_prevt, intstor_op, intstor_op_prevt, intstor_up, intstor_up_prevt, theta_uz, theta_uz_prevt,
            sc_gw, gwl_prevt, gwl, gwl_sl, gwl_sl_prevt, so_swds, so_swds_prevt, so_mss, so_mss_prevt, stor_swds, stor_swds_prevt,
            stor_mss, stor_mss_prevt, owl_prevt, owl, intstor_meas, intstor_meas_prevt, top_stor_meas, top_stor_meas_prevt, bot_stor_meas,
            bot_stor_meas_prevt, meas_ow, meas_gw, meas_swds):
        """
        Calculates states and fluxes during current time step

        Args:

        Returns:
        """
        # this part is  the water balance for the main body. So the water balance is evaluated on the [mm/area]
        rainfall_tot = P_atm

        evaporation_tot = (e_atm_pr * self.pr_no_meas_area + e_atm_cp * self.cp_no_meas_area + e_atm_op * self.op_no_meas_area \
                          + e_atm_up * self.up_no_meas_area + e_atm_ow * self.ow_no_meas_area + t_atm_uz * self.uz_no_meas_area + \
                          e_atm_meas * self.meas_area + tt_atm_meas * self.meas_top_area + tb_atm_meas * self.meas_bot_area) / self.tot_area

        seepage_tot = s_gw_out * self.gw_no_meas_area / self.tot_area

        drainage_tot = d_gw_ow * self.gw_no_meas_area / self.tot_area

        sewerflow_tot = (q_swds_ow * self.swds_no_meas_area + q_mss_ow * self.mss_no_meas_area + sum_so_ow * self.ow_no_meas_area) / self.tot_area

        toWWTP_tot = q_mss_out * self.mss_no_meas_area / self.tot_area

        OWtoOut_tot = q_ow_out + q_meas_out * self.meas_bot_area

        StorChange_tot = ((intstor_pr - intstor_pr_prevt) * self.pr_no_meas_area + (intstor_cp - intstor_cp_prevt) * \
                         self.cp_no_meas_area + (intstor_op - intstor_op_prevt) * self.op_no_meas_area + (intstor_up - intstor_up_prevt) * \
                         self.up_no_meas_area + (theta_uz - theta_uz_prevt) * self.uz_no_meas_area + 1000 * sc_gw * (gwl_prevt - gwl) * \
                         self.gw_no_meas_area + (gwl_sl - gwl_sl_prevt) * self.gw_no_meas_area + \
                         (((so_swds - so_swds_prevt) * self.swds_no_meas_area + (so_mss - so_mss_prevt) * self.mss_no_meas_area) if self.ow_no_meas_area==0 else 0) + \
                         (stor_swds - stor_swds_prevt) * self.swds_no_meas_area + (stor_mss - stor_mss_prevt) * self.mss_no_meas_area + \
                         1000 * (owl_prevt- owl) * self.ow_no_meas_area + (intstor_meas - intstor_meas_prevt) * self.meas_area + \
                         (top_stor_meas - top_stor_meas_prevt) * self.meas_top_area + (bot_stor_meas - bot_stor_meas_prevt) * self.meas_bot_area)/self.tot_area

        BalanceClosed_tot = rainfall_tot - evaporation_tot - seepage_tot - toWWTP_tot - ((drainage_tot + sewerflow_tot) if self.ow_no_meas_area==0 else OWtoOut_tot) - StorChange_tot

        # this part is the water balance check for the measure and its inflow area. So the water balance is evaluated on the [mm/ inflow area]
        # mia is the abbreviation for measure inflow area
        # for this part, the calculations should be adaptive to the area where the measure is applied.
        rainfall_mia = P_atm

        # Currently two situations： a. inflow area = measure area b. inflow area = op(pr) area where the measure is applied. (see diifferent exp for a measure where inflow = meas < op area)
        # Think about how to do: 1. if inflow area is somewhere between the two 2. if contains inflow area from multiple sources
        if self.inflowareaIsoparea:
            evaporation_mia = (e_atm_meas * self.meas_area + tt_atm_meas * self.meas_top_area + tb_atm_meas * self.meas_bot_area + \
                               e_atm_op * self.op_no_meas_area)/ self.op_meas_inflow_area # this part --- e_atm_op is related to the area where the measure is applied.

            storage_mia = (intstor_meas * self.meas_area + top_stor_meas * self.meas_top_area + bot_stor_meas * self.meas_bot_area +
                        intstor_op * self.op_no_meas_area) / self.op_meas_inflow_area # this part --- intstor_op is related to the area where the measure is applied.
        else:
            evaporation_mia = (e_atm_meas * self.meas_area + tt_atm_meas * self.meas_top_area + tb_atm_meas * self.meas_bot_area)/self.op_meas_inflow_area

            storage_mia = (intstor_meas * self.meas_area + top_stor_meas * self.meas_top_area + bot_stor_meas * self.meas_bot_area)/self.op_meas_inflow_area

        toOW_mia = meas_ow * self.meas_area / self.op_meas_inflow_area

        toGW_mia = meas_gw * self.meas_area /self.op_meas_inflow_area

        runofftoSWDS_mia = meas_swds * self.meas_area / self.op_meas_inflow_area

        return {"rainfall_tot": rainfall_tot, "evaporation_tot": evaporation_tot, "seepage_tot":seepage_tot,
                "drainage_tot": drainage_tot, "sewerflow_tot":sewerflow_tot, "toWWTP_tot":toWWTP_tot,
                "OWtoOut_tot": OWtoOut_tot, "StorChange_tot":StorChange_tot, "BalanceClosed_tot":BalanceClosed_tot,
                "rainfall_mia": rainfall_mia, "evaporation_mia": evaporation_mia, "storage_mia":storage_mia,
                "toOW_mia": toOW_mia, "toGW_mia":toGW_mia, "runofftoSWDS_mia":runofftoSWDS_mia}





