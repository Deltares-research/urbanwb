#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from urbanwb.selector import soil_selector
from urbanwb.gwlcalculator import gwlcalc


class Groundwater:
    """
    creates an instance of Groundwater class with given initial states and properties, iterates sol() function to
    compute states and fluxes of groundwater at each time step.

    Args:
        gwl_t0 (float): initial groundwater level (at t=0) [m-SL]
        gw_no_meas_area (float): area of groundwater without measure [m^2]
        gw_meas_area (float): area of groundwater with measure [m^2]
        seepage_define (int): seepage to deep groundwater defined as either constant downward flux or dynamic computed \
        flux which is determined by head difference and resistance [0=flux; 1=level]
        w (float): drainage resistance from groundwater to open water [d]
        vc (float): vertical flow resistance from shallow groundwater to deep groundwater [d]
        head_deep_gw (float): predefined hydraulic head of deep groundwater [m-SL]
        down_seepage_flux (float): predefined constant downward flux from shallow groundwater to deep groundwater [mm/d]
        soiltype (int): soil type
        croptype (int): crop type
    """

    def __init__(
        self,
        gwl_t0,
        gw_no_meas_area,
        gw_meas_area,
        seepage_define=0,
        w=100,
        vc=20000,
        head_deep_gw=21.5,
        down_seepage_flux=1,
        soiltype=2,
        croptype=1,
        **kwargs
    ):

        # state

        # self.gwl_prevt (float): groundwater level at previous time step [m-SL]
        self.gwl_prevt = gwl_t0
        # self.gwl_sl_prevt (float): groundwater level above surface level at previous time step [m-SL]
        self.gwl_sl_prevt = 0

        # properties

        self.gw_no_meas_area = gw_no_meas_area
        self.gw_meas_area = gw_meas_area
        self.seepage_define = seepage_define
        self.w = w
        self.vc = vc
        self.head_deep_gw = head_deep_gw
        self.down_seepage_flux = down_seepage_flux
        self.soiltype = soiltype
        self.croptype = croptype

        # self.soil_prm (dataframe): soil parameter matrix dependent on soil type and crop type
        self.soil_prm = soil_selector(self.soiltype, self.croptype)

    def sol(
        self,
        p_uz_gw,
        uz_no_meas_area,
        p_op_gw,
        op_no_meas_area,
        tot_meas_area,
        meas_gw,
        owl_prevt,
        delta_t=1 / 24,
    ):
        """
        Calculates states and fluxes in groundwater during current time step.

        Args:
            p_uz_gw (float): percolation from unsaturated zone to groundwater during current time step [mm]
            uz_no_meas_area (float): area of unsaturated zone without measure [m^2]
            p_op_gw (float): percolation from open paved to groundwater during current time step [mm]
            op_no_meas_area (float): area of open paved without measure [m^2]
            tot_meas_area (float): total area of measure [m^2]
            meas_gw (float): inflow from measure to groundwater during current time step [mm]
            owl_prevt (float): open water level at previous time step [m-SL]
            delta_t (float): length of time step [d]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of groundwater during current time step:

            * **sum_p_gw** -- Sum of percolation from unsaturated zone and percolation from open paved to groundwater during current time step [mm]
            * **r_meas_gw** -- Inflow from measure (if applicable) to groundwater during current time step [mm]
            * **gwl_up** -- First value in predefined lookup table above groundwater level at the end of previous time step [m-SL]
            * **gwl_low** -- First value in predefined lookup table below groundwater level at the end of previous time step [m-SL]
            * **sc_gw** -- Storage coefficient of groundwater for current time step [-]
            * **h_gw** -- Groundwater level at the end of current time step [m-SL]
            * **s_gw_out** -- Downward seepage from shallow groundwater to deep groundwater during current time step [mm]
            * **d_gw_ow**  -- Groundwater drainage to open water during current time step [mm]
            * **gwl** -- Groundwater level below surface level at the end of current time step [m-SL]
            * **gwl_sl** -- Groundwater level above surface level at the end of current time step [m-SL]

        """

        if self.gw_no_meas_area == 0.0:
            sum_p_gw = (
                r_meas_gw
            ) = sc_gw = h_gw = s_gw_out = d_gw_ow = gwl = gwl_sl = 0.0
        else:
            sum_p_gw = (
                p_uz_gw * uz_no_meas_area + p_op_gw * op_no_meas_area
            ) / self.gw_no_meas_area

            r_meas_gw = meas_gw * tot_meas_area / self.gw_no_meas_area

            if uz_no_meas_area == 0.0:  # note div0 error!
                gwl_up = gwl_low = 0.0
            else:
                gwl_sol = gwlcalc(self.gwl_prevt)
                gwl_up = gwl_sol[0]
                gwl_low = gwl_sol[1]
                id1 = gwl_sol[2]
                id2 = gwl_sol[3]

            if self.gwl_prevt < 10.0:
                sc_gw = self.soil_prm[id2]["stor_coef"] + (gwl_low - self.gwl_prevt) / (
                    gwl_low - gwl_up
                ) * (self.soil_prm[id1]["stor_coef"] - self.soil_prm[id2]["stor_coef"])
            else:
                sc_gw = self.soil_prm[29]["stor_coef"]

            if self.seepage_define > 0.5:
                h_gw = -(
                    (
                        (sum_p_gw + r_meas_gw) / delta_t / 1000.0 * self.w * self.vc
                        - self.head_deep_gw * self.w
                        - owl_prevt * self.vc
                    )
                    / (self.w + self.vc)
                    + (
                        -(self.gwl_prevt + self.gwl_sl_prevt)
                        - (
                            (sum_p_gw + r_meas_gw) / delta_t / 1000.0 * self.w * self.vc
                            - self.head_deep_gw * self.w
                            - owl_prevt * self.vc
                        )
                        / (self.w + self.vc)
                    )
                    * np.exp(-delta_t * (self.w + self.vc) / (sc_gw * self.w * self.vc))
                )

                s_gw_out = (
                    1000.0
                    * (
                        self.head_deep_gw
                        - 0.5 * (h_gw + (self.gwl_prevt + self.gwl_sl_prevt))
                    )
                    / self.vc
                    * delta_t
                )

            else:
                h_gw = -(
                    self.w
                    * (
                        ((sum_p_gw + r_meas_gw) / delta_t - self.down_seepage_flux)
                        / 1000.0
                    )
                    - owl_prevt
                    + (
                        -(self.gwl_prevt + self.gwl_sl_prevt)
                        - (
                            self.w
                            * (
                                (
                                    (sum_p_gw + r_meas_gw) / delta_t
                                    - self.down_seepage_flux
                                )
                                / 1000.0
                            )
                            - owl_prevt
                        )
                    )
                    * np.exp(-delta_t / (sc_gw * self.w))
                )

                s_gw_out = delta_t * self.down_seepage_flux

            d_gw_ow = (
                sum_p_gw
                + r_meas_gw
                - s_gw_out
                - sc_gw
                * (self.gwl_prevt + self.gwl_sl_prevt / sc_gw - h_gw)
                * 1000.0  # div sc_gw
            )

            gwl = max(
                0.0,
                self.gwl_prevt
                + self.gwl_sl_prevt / sc_gw  # add gwl_sl (t-1) / sc
                - (sum_p_gw + r_meas_gw - s_gw_out - d_gw_ow) / (1000.0 * sc_gw),
            )

            gwl_sl = -1.0 * max(
                0.0,
                (
                    0.0
                    - (
                        self.gwl_prevt
                        + self.gwl_sl_prevt / sc_gw  # add gwl_sl (t-1) / sc
                        - (sum_p_gw + r_meas_gw - s_gw_out - d_gw_ow) / (1000.0 * sc_gw)
                    )
                )
                * sc_gw,
            )

            # update state
            self.gwl_prevt = gwl
            self.gwl_sl_prevt = gwl_sl

        return {
            "sum_p_gw": sum_p_gw,
            "r_meas_gw": r_meas_gw,
            "sc_gw": sc_gw,
            "h_gw": h_gw,
            "s_gw_out": s_gw_out,
            "d_gw_ow": d_gw_ow,
            "gwl": gwl,
            "gwl_sl": gwl_sl,
        }
