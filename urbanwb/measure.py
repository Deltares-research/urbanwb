#! /usr/bin/env python
# -*- coding: utf-8 -*-


class Measure:
    """
    Creates an instance of Measure class with given initial states and properties, iterates sol() function to compute
    states and fluxes of measure at each time step.

    Args:
        tot_meas_area (float): total area of measure [m^2]
        num_stor_lvl (int): predefined number of storage layers [1, 2 or 3]
        runoff_to_stor_layer (int): predefined selection at which measure layer runoff from other area is stored, inflow \
        runoff can only take place at interception layer (1) or at bottom storage layer (3) [1 or 3]

        # Active processes:
        EV_evaporation (int): predefined selection if evaporation from measure interception layer is possible (1) or not (0) [0 or 1]
        ET_transpiration (int): predefined selection if evapotranspiration from measure is possible (1) or not (0) [0 or 1]
        IN_infiltration (int): predefined selection if infiltration from measure is possible (1) or not (0) [0 or 1]
        SD_delay (int): predefined selection if slow drainage from measure is possible (1) or not (0) [0 or 1]
        FD_pumping (int): predefined selection if fast drainage from measure is possible (1) or not (0) [0 or 1]
        # RTC_realtime (int): predefined selection if real-time-control release from measure is possible (1) or not (0) [0 or 1]

        # Interception layer:
        storcap_int_meas (float): predefined storage capacity of interception layer of measure [mm]
        infilcap_int_meas (float): predefined infiltration capacity of interception layer of measure [mm/d]
        stor_int_meas_t0 (float): initial storage in interception layer of measure (at t=0) [mm]

        # Top storage layer:
        top_meas_area (float): predefined area of top storage layer of measure [m^2]
        storcap_top_meas (float): predefined storage capacity of top storage layer of measure [mm]
        infilcap_top_meas (float): predefined infiltration capacity of top storage layer of measure [mm/d]
        stor_top_meas_t0 (float): initial storage in top storage layer of measure (at t=0) [mm]

        # Bottom storage layer:
        btm_meas_area (float): predefined area of bottom storage layer of measure [m^2]
        storcap_btm_meas (float): predefined storage capacity of bottom storage layer of measure [mm]
        connection_to_gw (int): predefined percolation (connection) from measure bottom storage layer to groundwater is possible (1) or not (0) [0 or 1]
        limited_by_gwl (int): predefined limitation of percolation from measure to groundwater if groundwater level is \
        below measure bottom level, limited (1) or unlimited (0) [0 or 1]
        btm_level_meas (float): predefined bottom level of measure [m-SL]
        btm_meas_transpiration (int): predefined selection if transpiration from bottom storage layer of measure is possible (1) or not (0) [0 or 1]
        btm_discharge_type (int): predefined discharge type from bottom storage layer of measure [0:flux or 1:level]
        runoffcap_btm_meas (float): predefined runoff capacity from bottom storage layer of measure [mm/d]
        dischlvl_btm_meas (float): predefined discharge level from bottom storage layer of measure [mm]
        c_btm_meas (float): predefined hydraulic resistance for level induced discharge from bottom storage layer of measure [d]
        k_sat_uz (float): saturation permeability of soil [mm/d]
        evaporation_factor_meas (float): predefined evaporation factor of measure [-]
        stor_btm_meas_t0 (float): initial storage in bottom storage layer of measure (at t=0) [mm]

        # Runoff from measure flows to:
        surf_runoff_meas_OW (int): predefined definition of surface runoff from measure storage 1 (interception level) to open water (0 = no, 1 = yes)
        ctrl_runoff_meas_OW (int): predefined definition of controlled runoff from measure storage 3 (bottom level) to open water (0 = no, 1 = yes)
        overflow_meas_OW (int): predefined definition of overflow from measure storage 3 (bottom level) to open water (0 = no, 1 = yes)
        surf_runoff_meas_UZ (int): predefined definition of surface runoff from measure storage 1 (interception level) to unsaturated zone (0 = no, 1 = yes)
        ctrl_runoff_meas_UZ (int): predefined definition of controlled runoff from measure to unsaturated zone (0 = no, 1 = yes)
        overflow_meas_UZ (int): predefined definition of overflow from measure to unsaturated zone (0 = no, 1 = yes)
        surf_runoff_meas_GW (int): predefined definition of surface runoff from measure to groundwater (0 = no, 1 = yes)
        ctrl_runoff_meas_GW (int): predefined definition of controlled runoff from measure to groundwater (0 = no, 1 = yes)
        overflow_meas_GW (int): predefined definition of overflow from measure to groundwater (0 = no, 1 = yes)
        surf_runoff_meas_SWDS (int): predefined definition of surface runoff from measure to storm water drainage system (0 = no, 1 = yes)
        ctrl_runoff_meas_SWDS (int): predefined definition of controlled runoff from measure to storm water drainage system (0 = no, 1 = yes)
        overflow_meas_SWDS (int): predefined definition of overflow from measure to storm water drainage system (0 = no, 1 = yes)
        surf_runoff_meas_MSS (int): predefined definition of surface runoff from measure to mixed sewer system (0 = no, 1 = yes)
        ctrl_runoff_meas_MSS (int): predefined definition of controlledrunoff from measure to mixed sewer system (0 = no, 1 = yes)
        overflow_meas_MSS (int): predefined definition of overflow from measure to mixed sewer system (0 = no, 1 = yes)
        surf_runoff_meas_Out (int): predefined definition of surface runoff from measure to outside water (0 = no, 1 = yes)
        ctrl_runoff_meas_Out (int): predefined definition of controlled runoff from measure to outside water (0 = no, 1 = yes)
        overflow_meas_Out (int): predefined definition of overflow from measure to outside water (0 = no, 1 = yes)
    """

    def __init__(self, tot_meas_area, runoff_to_stor_layer, intstor_meas_t0, EV_evaporation, num_stor_lvl, infilcap_int_meas,
                 storcap_top_meas, storcap_btm_meas, stor_top_meas_t0, stor_btm_meas_t0, storcap_int_meas, top_meas_area,
                 ET_transpiration, evaporation_factor_meas, IN_infiltration, infilcap_top_meas, btm_meas_area, btm_meas_transpiration, connection_to_gw, limited_by_gwl,
                 k_sat_uz, btm_level_meas, btm_discharge_type, runoffcap_btm_meas, dischlvl_btm_meas, c_btm_meas, surf_runoff_meas_OW, ctrl_runoff_meas_OW,
                 overflow_meas_OW, surf_runoff_meas_UZ, ctrl_runoff_meas_UZ, overflow_meas_UZ, surf_runoff_meas_GW, ctrl_runoff_meas_GW, overflow_meas_GW, surf_runoff_meas_SWDS,
                 ctrl_runoff_meas_SWDS, overflow_meas_SWDS, surf_runoff_meas_MSS, ctrl_runoff_meas_MSS, overflow_meas_MSS, surf_runoff_meas_Out, ctrl_runoff_meas_Out, overflow_meas_Out, greenroof_type_measure, **kwargs):
        """
        Creates an instance of Measure class.
        """

        self.tot_meas_area = tot_meas_area
        self.num_stor_lvl = num_stor_lvl
        self.runoff_to_stor_layer = runoff_to_stor_layer

        # active processes
        self.EV_evaporation = EV_evaporation
        self.ET_transpiration = ET_transpiration
        self.IN_infiltration = IN_infiltration
        # self.SD_delay = SD_delay
        # self.FD_pumping = FD_pumping

        # interception layer
        self.storcap_int_meas = storcap_int_meas
        self.infilcap_int_meas = infilcap_int_meas
        # self.intstor_meas_prevt (float): storage in interception layer at the end of previous time step [mm]
        self.intstor_meas_prevt = intstor_meas_t0

        # top storage layer
        self.top_meas_area = top_meas_area
        self.storcap_top_meas = storcap_top_meas
        self.infilcap_top_meas = infilcap_top_meas
        # self.stor_top_meas_prevt (float): storage in top storage layer at the end of previous time step [mm]
        self.stor_top_meas_prevt = stor_top_meas_t0

        # bottom storage layer
        self.btm_meas_area = btm_meas_area
        self.storcap_btm_meas = storcap_btm_meas
        self.connection_to_gw = connection_to_gw
        self.limited_by_gwl = limited_by_gwl
        self.btm_level_meas = btm_level_meas
        self.btm_meas_transpiration = btm_meas_transpiration
        self.btm_discharge_type = btm_discharge_type
        self.runoffcap_btm_meas = runoffcap_btm_meas
        self.dischlvl_btm_meas = dischlvl_btm_meas
        self.c_btm_meas = c_btm_meas
        # self.stor_btm_meas_prevt (float): storage in bottom storage layer at the end of previous time step [mm]
        self.stor_btm_meas_prevt = stor_btm_meas_t0
        self.evaporation_factor_meas = evaporation_factor_meas
        self.k_sat_uz = k_sat_uz

        # water from measure flows to
        self.surf_runoff_meas_OW = surf_runoff_meas_OW
        self.ctrl_runoff_meas_OW = ctrl_runoff_meas_OW
        self.overflow_meas_OW = overflow_meas_OW
        self.surf_runoff_meas_UZ = surf_runoff_meas_UZ
        self.ctrl_runoff_meas_UZ = ctrl_runoff_meas_UZ
        self.overflow_meas_UZ = overflow_meas_UZ
        self.surf_runoff_meas_GW = surf_runoff_meas_GW
        self.ctrl_runoff_meas_GW = ctrl_runoff_meas_GW
        self.overflow_meas_GW = overflow_meas_GW
        self.surf_runoff_meas_SWDS = surf_runoff_meas_SWDS
        self.ctrl_runoff_meas_SWDS = ctrl_runoff_meas_SWDS
        self.overflow_meas_SWDS = overflow_meas_SWDS
        self.surf_runoff_meas_MSS = surf_runoff_meas_MSS
        self.ctrl_runoff_meas_MSS = ctrl_runoff_meas_MSS
        self.overflow_meas_MSS = overflow_meas_MSS
        self.surf_runoff_meas_Out = surf_runoff_meas_Out
        self.ctrl_runoff_meas_Out = ctrl_runoff_meas_Out
        self.overflow_meas_Out = overflow_meas_Out
        self.greenroof_type_measure = greenroof_type_measure

    def sol(self, p_atm, e_pot_ow, r_pr_meas, r_cp_meas, r_op_meas, r_up_meas, pr_no_meas_area, cp_no_meas_area,
            op_no_meas_area, up_no_meas_area, gw_no_meas_area, gwl_prevt, delta_t,
            ):
        """
        Calculates states and fluxes in measure during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]
            r_pr_meas (float): runoff from paved roof to measure during current time step [mm]
            r_cp_meas (float): runoff from closed paved to measure during current time step [mm]
            r_op_meas (float): runoff from open paved to measure during current time step [mm]
            r_up_meas (float): runoff from unpaved to measure during current time step [mm]
            pr_no_meas_area (float): area of paved roof without measure [m^2]
            cp_no_meas_area (float): area of closed pave without measure [m^2]
            op_no_meas_area (float): area of open paved without measure [m^2]
            up_no_meas_area (float): area of unpaved without measure [m^2]
            gw_no_meas_area (float): area of groundwater without measure [m^2]
            gwl_prevt (float): groundwater level at previous time step [m-SL]
            delta_t (float): length of time step [d]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of measure during current time step:

            * **prec_meas** -- Direct rainfall on measure during current time step [mm]
            * **sum_r_meas** -- Total runoff from paved roof, closed paved, open paved, unpaved to measure during current time step [mm]
            * **int_meas** -- Interception storage on interception layer of measure after rainfall at the beginning of current time step [mm]
            * **e_atm_meas** -- Evaporation form interception layer of measure during current time step [mm]
            * **interc_down_meas** -- Downward flow from interception layer of measure during current time step [mm]
            * **surf_runoff_meas** -- Surface runoff from interception layer of measure during current time step [mm]
            * **intstor_meas** -- Remaining interception storage on interception layer of measure during current time step [mm]
            * **ini_stor_top_meas** -- Storage in top storage layer of measure at the beginning of current time step [mm]
            * **t_atm_top_meas** -- Transpiration from top storage layer of measure during current time step [mm]
            * **perc_top_meas** -- Percolation from top layer of measure at the current time step [mm]
            * **fin_stor_top_meas** -- top layer storage at the end of current time step [mm]
            * **ini_stor_btm_meas** -- bottom layer storage at the beginning of current time step [mm]
            * **t_atm_btm_meas** -- transpiration from bottom layer of measure at the current time step [mm]
            * **p_gw_btm_meas** -- percolation from bottom layer of measure to groundwater during current time step [mm]
            * **runoff_btm_meas** -- runoff from the bottom layer of the measure during current time step [mm]
            * **fin_stor_btm_meas** -- bottom storage at the end of the current time step [mm]
            * **overflow_btm_meas** -- bottom storage overflow during current time step [mm]
            * **q_meas_ow** -- Measure outflow to open water during current time step [mm]
            * **q_meas_uz** -- Measure outflow to unsaturated zone during current time step [mm]
            * **q_meas_gw** -- Measure outflow to groundwater during current time step [mm]
            * **q_meas_swds** -- Measure outflow to storm water drainage system during current time step [mm]
            * **q_meas_mss** -- Measure outflow to mixed sewer system during current time step [mm]
            * **q_meas_out** -- Measure outflow to outside water during current time step [mm]
        """

        if self.tot_meas_area == 0:
            prec_meas = sum_r_meas = int_meas = e_atm_meas = interc_down_meas = surf_runoff_meas = intstor_meas = \
                ini_stor_top_meas = t_atm_top_meas = perc_top_meas = fin_stor_top_meas = ini_stor_btm_meas = \
                t_atm_btm_meas = p_gw_btm_meas = runoff_btm_meas = fin_stor_btm_meas = overflow_btm_meas = q_meas_ow = \
                q_meas_uz = q_meas_gw = q_meas_swds = q_meas_mss = q_meas_out = 0.0
            # uncontrolled_runoff = controlled_runoff = total_runoff = 0.0

        else:
            prec_meas = p_atm

            sum_r_meas = (r_pr_meas * pr_no_meas_area + r_cp_meas * cp_no_meas_area + r_op_meas * op_no_meas_area +
                          r_up_meas * up_no_meas_area) / self.tot_meas_area

            int_meas = self.intstor_meas_prevt + prec_meas + (sum_r_meas if self.runoff_to_stor_layer == 1 else 0.0)

            e_atm_meas = self.EV_evaporation * min(int_meas, e_pot_ow)

            if self.num_stor_lvl > 1.5:

                if not self.greenroof_type_measure:

                    interc_down_meas = max(0.0, min(int_meas - e_atm_meas, delta_t * self.infilcap_int_meas,
                                               ((self.storcap_top_meas - self.stor_top_meas_prevt) if self.num_stor_lvl > 2.5 else
                                         (self.storcap_btm_meas - self.stor_btm_meas_prevt))))
                else:
                    interc_down_meas = max(0.0, min(int_meas - e_atm_meas - self.storcap_int_meas, delta_t * self.infilcap_int_meas))

            else:

                interc_down_meas = 0.0

            surf_runoff_meas = max(0.0, int_meas - e_atm_meas - interc_down_meas - self.storcap_int_meas)

            intstor_meas = max(0.0, int_meas - e_atm_meas - interc_down_meas - surf_runoff_meas)

            if self.num_stor_lvl < 2.5:
                ini_stor_top_meas = 0.0
            else:
                ini_stor_top_meas = 0.0 if self.top_meas_area == 0.0 else self.stor_top_meas_prevt + interc_down_meas * (self.tot_meas_area / self.top_meas_area)

            t_atm_top_meas = 0.0 if self.num_stor_lvl < 2.5 else self.ET_transpiration * min(ini_stor_top_meas, self.evaporation_factor_meas * e_pot_ow)

            if self.num_stor_lvl < 2.5:

                perc_top_meas = 0.0

            else:
                if not self.greenroof_type_measure:
                    perc_top_meas = max(0.0, min(ini_stor_top_meas - t_atm_top_meas, delta_t * self.infilcap_top_meas))
                else:
                    perc_top_meas = max(0.0, min(ini_stor_top_meas - t_atm_top_meas - self.storcap_top_meas, delta_t *
                                                 self.infilcap_top_meas))

            # perc_top_meas = 0.0 if self.num_stor_lvl < 2.5 else max(0, min(ini_stor_top_meas - t_atm_top_meas, delta_t * self.infilcap_top_meas))

            fin_stor_top_meas = min(self.storcap_top_meas, ini_stor_top_meas - t_atm_top_meas - perc_top_meas)

            if self.num_stor_lvl < 1.5:
                ini_stor_btm_meas = 0.0
            else:
                if self.btm_meas_area == 0.0:
                    ini_stor_btm_meas = 0.0
                else:
                    ini_stor_btm_meas = self.stor_btm_meas_prevt + \
                                  (0.0 if self.runoff_to_stor_layer == 1 else sum_r_meas) + \
                                  ((interc_down_meas * (self.tot_meas_area / self.btm_meas_area)) if self.num_stor_lvl < 2.5 else (perc_top_meas * (self.top_meas_area / self.btm_meas_area)))

            if self.btm_meas_transpiration < 0.5:
                t_atm_btm_meas = 0.0
            else:
                if self.num_stor_lvl < 2.5:
                    t_atm_btm_meas = self.ET_transpiration * min(ini_stor_btm_meas, self.evaporation_factor_meas * e_pot_ow)
                else:
                    t_atm_btm_meas = self.ET_transpiration * min(ini_stor_btm_meas, self.evaporation_factor_meas * e_pot_ow - t_atm_top_meas)

            if self.connection_to_gw < 0.5:
                p_gw_btm_meas = 0.0
            else:
                if self.limited_by_gwl < 0.5:
                    p_gw_btm_meas = max(0.0, min(ini_stor_btm_meas - t_atm_btm_meas, delta_t * self.k_sat_uz))
                else:
                    if gwl_prevt < self.btm_level_meas:
                        p_gw_btm_meas = 0.0
                    else:
                        p_gw_btm_meas = min(0.0 if self.btm_meas_area == 0.0 else 1000.0 * (gwl_prevt - self.btm_level_meas) * (gw_no_meas_area / self.btm_meas_area), max(0.0, min(ini_stor_btm_meas - t_atm_btm_meas, delta_t * self.k_sat_uz)))

            if self.btm_discharge_type < 0.5:
                runoff_btm_meas = min(delta_t * self.runoffcap_btm_meas, ini_stor_btm_meas - t_atm_btm_meas - p_gw_btm_meas)
            else:
                if self.c_btm_meas == 0.0:
                    runoff_btm_meas = min(max(0.0, ini_stor_btm_meas - t_atm_btm_meas - p_gw_btm_meas - self.dischlvl_btm_meas), 0.0)
                else:
                    runoff_btm_meas = min(max(0.0, ini_stor_btm_meas - t_atm_btm_meas - p_gw_btm_meas - self.dischlvl_btm_meas), delta_t * max(0.0, (ini_stor_btm_meas - t_atm_btm_meas - p_gw_btm_meas - self.dischlvl_btm_meas)) / self.c_btm_meas)

            fin_stor_btm_meas = min(self.storcap_btm_meas, ini_stor_btm_meas - t_atm_btm_meas - p_gw_btm_meas - runoff_btm_meas)

            overflow_btm_meas = max(0.0, ini_stor_btm_meas - t_atm_btm_meas - p_gw_btm_meas - runoff_btm_meas - fin_stor_btm_meas)

            q_meas_ow = self.surf_runoff_meas_OW * surf_runoff_meas + (0.0 if self.btm_meas_area == 0.0 else (self.ctrl_runoff_meas_OW * runoff_btm_meas + self.overflow_meas_OW * overflow_btm_meas) * self.tot_meas_area / self.btm_meas_area)

            q_meas_uz = self.surf_runoff_meas_UZ * surf_runoff_meas + (0.0 if self.btm_meas_area == 0.0 else (self.ctrl_runoff_meas_UZ * runoff_btm_meas + self.overflow_meas_UZ * overflow_btm_meas) * self.tot_meas_area / self.btm_meas_area)

            q_meas_gw = self.surf_runoff_meas_GW * surf_runoff_meas + (0.0 if self.btm_meas_area == 0.0 else (p_gw_btm_meas + self.ctrl_runoff_meas_GW * runoff_btm_meas + self.overflow_meas_GW * overflow_btm_meas) * self.tot_meas_area / self.btm_meas_area)

            q_meas_swds = self.surf_runoff_meas_SWDS * surf_runoff_meas + (0.0 if self.btm_meas_area == 0.0 else (self.ctrl_runoff_meas_SWDS * runoff_btm_meas + self.overflow_meas_SWDS * overflow_btm_meas) * self.tot_meas_area / self.btm_meas_area)

            q_meas_mss = self.surf_runoff_meas_MSS * surf_runoff_meas + (0.0 if self.btm_meas_area == 0.0 else (self.ctrl_runoff_meas_MSS * runoff_btm_meas + self.overflow_meas_MSS * overflow_btm_meas) * self.tot_meas_area / self.btm_meas_area)

            q_meas_out = self.surf_runoff_meas_Out * surf_runoff_meas + (0.0 if self.btm_meas_area == 0.0 else (self.ctrl_runoff_meas_Out * runoff_btm_meas + self.overflow_meas_Out * overflow_btm_meas) * self.tot_meas_area / self.btm_meas_area)

            # # add controlled runoff, uncontrolled runoff and total runoff (to be developed)
            # # uncontrolled runoff is bottom overflow plus surface overflow
            # # controlled runoff is bottom controlled runoff
            # uncontrolled_runoff = surf_runoff_meas + overflow_btm_meas
            # controlled_runoff = runoff_btm_meas
            # total_runoff = uncontrolled_runoff + controlled_runoff

            # update state:
            # update interception storage
            self.intstor_meas_prevt = intstor_meas
            self.stor_top_meas_prevt = fin_stor_top_meas
            self.stor_btm_meas_prevt = fin_stor_btm_meas

        return {"prec_meas": prec_meas, "sum_r_meas": sum_r_meas, "int_meas": int_meas, "e_atm_meas": e_atm_meas,
                "interc_down_meas": interc_down_meas, "surf_runoff_meas": surf_runoff_meas, "intstor_meas": intstor_meas,
                "ini_stor_top_meas": ini_stor_top_meas, "t_atm_top_meas": t_atm_top_meas, "perc_top_meas": perc_top_meas,
                "fin_stor_top_meas": fin_stor_top_meas, "ini_stor_btm_meas": ini_stor_btm_meas, "t_atm_btm_meas": t_atm_btm_meas,
                "p_gw_btm_meas": p_gw_btm_meas, "runoff_btm_meas": runoff_btm_meas, "fin_stor_btm_meas": fin_stor_btm_meas, "overflow_btm_meas": overflow_btm_meas,
                "q_meas_ow": q_meas_ow, "q_meas_uz": q_meas_uz, "q_meas_gw": q_meas_gw,
                "q_meas_swds": q_meas_swds, "q_meas_mss": q_meas_mss, "q_meas_out": q_meas_out,
                #"uncontrolled_runoff": uncontrolled_runoff,
                #"controlled_runoff": controlled_runoff,
                #"total_runoff": total_runoff,
                }



