from urbanwb.selector import soil_selector
from urbanwb.unsaturatedzone import UnsaturatedZone


class Unpaved:
    """Creates an instance of Unpaved class with given initial states and properties, iterates sol() function to compute
    states and fluxes of unpaved at each time step.

    Args:
        fin_intstor_up_t0: initial final remaining interception storage on unpaved (at t=0) [mm]
        up_no_meas_area (float): area of unpaved without measure [m^2]
        up_meas_area (float): area of unpaved with measure [m^2]
        up_meas_inflow_area (float): measure inflow area from unpaved, i.e. runoff inflow area to measure from unpaved \
        (>= area of unpaved with measure and <= total area of unpaved) [m^2]
        intstorcap_up (float): predefined interception storage capacity on unpaved [mm]
        infilcap_up (float): predefined infiltration capacity on unpaved [mm/d]
        soiltype (int): soil type
        croptype (int): crop type

    """

    def __init__(
        self,
        fin_intstor_up_t0,
        up_no_meas_area,
        up_meas_area,
        up_meas_inflow_area,
        intstorcap_up=20,
        infilcap_up=48,
        soiltype=2,
        croptype=1,
        **kwargs,
    ):
        """Creates an instance of Unpaved class."""
        # state

        # self.fin_intstor_up_prevt (float): final remaining interception storage on unpaved at previous time step [mm]
        self.fin_intstor_up_prevt = fin_intstor_up_t0

        # properties

        self.up_no_meas_area = up_no_meas_area
        self.up_meas_area = up_meas_area
        self.up_meas_inflow_area = up_meas_inflow_area
        self.intstorcap_up = intstorcap_up
        self.infilcap_up = infilcap_up
        self.soiltype = soiltype
        self.croptype = croptype

        # self.soil_prm (dataframe): soil parameter matrix (only at gwl=0) dependent on soil type and crop type
        self.soil_prm = soil_selector(self.soiltype, self.croptype)[0]

        # self.max_moist_cont_uz: maximum moisture content of root zone [mm]
        self.max_moist_cont_uz = self.soil_prm["moist_cont_eq_rz[mm]"]

        # self.k_sat_uz: predefined saturated permeability of soil [mm/d]
        self.k_sat_uz = 10 * self.soil_prm["k_sat"]

        # self.inflowfac_up (float): measure inflow factor of unpaved [-]
        self.inflowfac_up = self.inflowfac()

    def inflowfac(self):
        """Calculates measure inflow factor of unpaved.

        Returns:
            (float): measure inflow factor of unpaved

            * **inflowfac** -- measure inflow factor is calculated as (runoff inflow area to measure from unpaved - \
            area of unpaved with measure) / area of unpaved without measure

        """
        if self.up_no_meas_area != 0.0:
            return (self.up_meas_inflow_area - self.up_meas_area) / self.up_no_meas_area
        else:
            return 0.0

    def sol(
        self,
        p_atm,
        e_pot_ow,
        r_pr_up,
        r_cp_up,
        r_op_up,
        theta_uz_prevt,
        pr_no_meas_area,
        cp_no_meas_area,
        op_no_meas_area,
        ow_no_meas_area,
        delta_t=1 / 24,
        irrigation=0.0,
    ):
        """Calculates states and fluxes on unpaved during current time step.

        Args:
            p_atm (float): rainfall during current time step [mm]
            e_pot_ow (float): potential open water evaporation during current time step [mm]
            r_pr_up (float): runoff from paved roof to unpaved during current time step [mm]
            r_cp_up (float): runoff from closed paved to unpaved during current time step [mm]
            r_op_up (float): runoff from open paved to unpaved during current time step [mm]
            theta_uz_prevt (float): moisture content of root zone at previous time step [mm]
            pr_no_meas_area (float): area of paved roof without measure [m^2]
            cp_no_meas_area (float): area of closed paved without measure [m^2]
            op_no_meas_area (float): area of open paved without measure [m^2]
            ow_no_meas_area (float): area of open water without measure [m^2]
            delta_t (float): length of time step [d]
            irrigation (float): garden water applied to the unpaved surface [mm/timestep]

        Returns:
            (dictionary): A dictionary of computed states and fluxes of unpaved during current time step:

            * **sum_r_up** -- Sum of runoff from all paved areas to unpaved during current time step [mm]
            * **init_intstor_up** -- Initial interception storage on unpaved after rainfall at the beginning of current time step [mm]
            * **actl_infilcap_up** -- Actual infiltration capacity on unpaved during current time step [mm]
            * **timefac_up** -- Time factor, i.e. part of time step that interception storage on unpaved is available \
            for infiltration and evaporation during current time step [-]
            * **e_atm_up** -- Evaporation from interception storage on unpaved during current time step [mm]
            * **i_up_uz** -- Infiltration from interception storage on unpaved to unsaturated zone during current time step [mm]
            * **fin_intstor_up** -- Final remaining interception storage on unpaved at the end of current time step [mm]
            * **r_up_meas** -- Runoff from unpaved to measure during current time step (not necessarily on unpaved itself) [mm]
            * **r_up_ow** -- Runoff from unpaved to open water during current time step [mm]

        """
        if self.up_no_meas_area == 0.0:
            sum_r_up = init_intstor_up = actl_infilcap_up = timefac_up = e_atm_up = (
                i_up_uz
            ) = fin_intstor_up = r_up_meas = r_up_ow = 0.0

        else:
            sum_r_up = (
                r_pr_up * pr_no_meas_area
                + r_cp_up * cp_no_meas_area
                + r_op_up * op_no_meas_area
            ) / self.up_no_meas_area

            init_intstor_up = self.fin_intstor_up_prevt + p_atm + sum_r_up + irrigation

            actl_infilcap_up = min(
                delta_t * self.infilcap_up,
                self.max_moist_cont_uz
                - theta_uz_prevt
                + min(self.max_moist_cont_uz - theta_uz_prevt, delta_t * self.k_sat_uz),
            )

            if e_pot_ow + actl_infilcap_up <= 0.0:
                timefac_up = 0.0
            else:
                timefac_up = min(1.0, init_intstor_up / (e_pot_ow + actl_infilcap_up))

            e_atm_up = timefac_up * e_pot_ow

            i_up_uz = timefac_up * actl_infilcap_up

            if ow_no_meas_area == 0.0:
                fin_intstor_up = max(
                    0.0,
                    min(
                        self.intstorcap_up
                        + (
                            self.up_no_meas_area
                            - (self.up_meas_inflow_area - self.up_meas_area)
                        )
                        / self.up_no_meas_area
                        * (init_intstor_up - e_atm_up - i_up_uz - self.intstorcap_up),
                        init_intstor_up - e_atm_up - i_up_uz,
                    ),
                )

            else:
                fin_intstor_up = max(
                    0.0, min(self.intstorcap_up, init_intstor_up - e_atm_up - i_up_uz)
                )

            r_up_meas = self.inflowfac_up * max(
                0.0, init_intstor_up - e_atm_up - i_up_uz - self.intstorcap_up
            )

            if ow_no_meas_area == 0.0:
                r_up_ow = 0.0
            else:
                r_up_ow = max(
                    0.0,
                    init_intstor_up
                    - e_atm_up
                    - i_up_uz
                    - self.intstorcap_up
                    - r_up_meas,
                )

            # update state
            self.fin_intstor_up_prevt = fin_intstor_up

        return {
            "sum_r_up": sum_r_up,
            "init_intstor_up": init_intstor_up,
            "actl_infilcap_up": actl_infilcap_up,
            "timefac_up": timefac_up,
            "e_atm_up": e_atm_up,
            "i_up_uz": i_up_uz,
            "fin_intstor_up": fin_intstor_up,
            "r_up_meas": r_up_meas,
            "r_up_ow": r_up_ow,
        }


class UnpavedAreas:
    """Separate irrigated and other unpaved stores with area-weighted outputs."""

    surface_columns = (
        "init_intstor_up", "fin_intstor_up", "e_atm_up", "i_up_uz",
        "r_up_meas", "r_up_ow",
    )
    root_columns = ("theta_uz", "t_atm_uz", "p_uz_gw")

    def __init__(self, parameters, garden_fraction, initial_theta):
        self.parameters = parameters
        self.fractions = {"garden": garden_fraction, "other_unpaved": 1 - garden_fraction}
        self.surfaces = {}
        self.rootzones = {}
        self.surface_solutions = {}
        self.root_solutions = {}
        for name, fraction in self.fractions.items():
            if fraction == 0:
                continue
            subset = dict(parameters)
            for area in ("up_no_meas_area", "up_meas_area", "up_meas_inflow_area", "uz_no_meas_area"):
                subset[area] *= fraction
            self.surfaces[name] = Unpaved(**subset)
            self.rootzones[name] = UnsaturatedZone(theta_uz_t0=initial_theta, **subset)
            self.surface_solutions[name] = dict.fromkeys(self.surface_columns, 0.0)
            self.surface_solutions[name]["fin_intstor_up"] = parameters["fin_intstor_up_t0"]
            self.root_solutions[name] = dict.fromkeys(self.root_columns, 0.0)
            self.root_solutions[name]["theta_uz"] = initial_theta

    def _aggregate(self, solutions):
        first = next(iter(solutions.values()))
        return {
            column: sum(self.fractions[name] * result[column] for name, result in solutions.items())
            for column in first
        }

    def surface_sol(self, **kwargs):
        for name, surface in self.surfaces.items():
            fraction = self.fractions[name]
            inputs = dict(kwargs)
            inputs["theta_uz_prevt"] = self.rootzones[name].theta_uz_prevt
            for area in ("pr_no_meas_area", "cp_no_meas_area", "op_no_meas_area"):
                inputs[area] *= fraction
            inputs["irrigation"] = kwargs.get("irrigation", 0.0) / fraction if name == "garden" else 0.0
            self.surface_solutions[name] = surface.sol(**inputs)
        return self._aggregate(self.surface_solutions)

    def sol(self, **kwargs):
        for name, rootzone in self.rootzones.items():
            inputs = dict(kwargs)
            inputs["i_up_uz"] = self.surface_solutions[name]["i_up_uz"]
            inputs["tot_meas_area"] *= self.fractions[name]
            self.root_solutions[name] = rootzone.sol(**inputs)
            rootzone.theta_uz_prevt = self.root_solutions[name]["theta_uz"]
        return self._aggregate(self.root_solutions)

    def limit_capillary_rise(self, solution, p_uz_gw):
        """Share a groundwater donor limit among only the capillary-rise requests."""
        reduction = p_uz_gw - solution["p_uz_gw"]
        available = sum(
            self.fractions[name] * max(0.0, -result["p_uz_gw"])
            for name, result in self.root_solutions.items()
        )
        if reduction < 0 or reduction > available + 1e-10:
            raise ValueError("Limited capillary rise must lie within the requested groundwater supply")
        if available > 0:
            factor = min(1.0, reduction / available)
            for name, result in self.root_solutions.items():
                if result["p_uz_gw"] < 0:
                    limited = result["p_uz_gw"] + factor * -result["p_uz_gw"]
                    self.rootzones[name].limit_capillary_rise(result, limited)
        solution.update(self._aggregate(self.root_solutions))
        solution["p_uz_gw"] = p_uz_gw

    def diagnostics(self):
        result = {}
        for name, fraction in self.fractions.items():
            result[f"{name}_area_m2"] = fraction * self.parameters["up_no_meas_area"]
            for column in self.surface_columns:
                result[f"{name}_{column}"] = self.surface_solutions.get(name, {}).get(column, 0.0)
            for column in self.root_columns:
                result[f"{name}_{column}"] = self.root_solutions.get(name, {}).get(column, 0.0)
        return result
