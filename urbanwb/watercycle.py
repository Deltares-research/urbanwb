import math

import pandas as pd


class WaterCycle:
    """Optional infrastructure accounting; all volumes are m3 per model step."""

    def __init__(self, parameters):
        self.config = dict(parameters.get("urban_water_cycle", {}))
        self.enabled = self.config.get("enabled", False)
        if not isinstance(self.enabled, bool):
            raise ValueError("urban_water_cycle.enabled must be a boolean")
        self.foul_storage = self.config.get("foul_initial_storage_m3", 0.0)
        self.wwtp_storage = self.config.get("wwtp_initial_storage_m3", 0.0)
        if not self.enabled:
            return
        allowed = {
            "enabled", "drinking_water", "sewer", "groundwater_infiltration",
            "wwtp", "sewer_system", "drinking_water_loss_percent",
            "indoor_return_fraction", "sewer_loss_percent", "sewer_depth_m",
            "sewer_entry_resistance_days", "foul_capacity_m3_day",
            "foul_storage_capacity_m3", "foul_initial_storage_m3",
            "wwtp_capacity_m3_day", "wwtp_residence_days",
            "wwtp_initial_storage_m3", "wwtp_local_fraction",
            "wwtp_inside_area", "timeseries",
            "mixed_capacity_m3_day", "garden_fraction",
        }
        unknown = self.config.keys() - allowed
        if unknown:
            raise ValueError(f"Unknown urban_water_cycle options: {sorted(unknown)}")
        for name in ("enabled", "drinking_water", "sewer", "groundwater_infiltration", "wwtp", "wwtp_inside_area"):
            if not isinstance(self.config.get(name, False), bool):
                raise ValueError(f"urban_water_cycle.{name} must be a boolean")
        for name, upper in (("drinking_water_loss_percent", 100), ("sewer_loss_percent", 100), ("indoor_return_fraction", 1), ("wwtp_local_fraction", 1), ("garden_fraction", 1)):
            value = self.config.get(name, 1.0 if name in ("indoor_return_fraction", "garden_fraction") else 0.0)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= upper:
                raise ValueError(f"urban_water_cycle.{name} must be between 0 and {upper}")
        if self.config.get("drinking_water_loss_percent", 0) == 100:
            raise ValueError("drinking_water_loss_percent must be less than 100")
        for name in ("sewer_depth_m", "sewer_entry_resistance_days", "foul_capacity_m3_day", "foul_storage_capacity_m3", "foul_initial_storage_m3", "wwtp_capacity_m3_day", "wwtp_residence_days", "wwtp_initial_storage_m3", "mixed_capacity_m3_day"):
            if name in self.config and (not isinstance(self.config[name], (int, float)) or isinstance(self.config[name], bool) or not math.isfinite(self.config[name]) or self.config[name] < 0):
                raise ValueError(f"urban_water_cycle.{name} must be finite and nonnegative")
        if self.config.get("sewer_system", "separated") not in ("mixed", "separated"):
            raise ValueError("sewer_system must be mixed or separated")
        if self.config.get("groundwater_infiltration", False):
            if not self.config.get("sewer", False):
                raise ValueError("groundwater_infiltration requires sewer")
            if "sewer_depth_m" not in self.config or self.config.get("sewer_entry_resistance_days", 0) <= 0:
                raise ValueError("Groundwater infiltration requires sewer_depth_m and a positive sewer_entry_resistance_days")
        if self.config.get("sewer_loss_percent", 0) and not self.config.get("sewer", False):
            raise ValueError("sewer_loss_percent requires sewer")
        if self.foul_storage > self.config.get("foul_storage_capacity_m3", math.inf):
            raise ValueError("Initial foul storage exceeds capacity")
        if self.uses("sewer"):
            separated = self.config.get("sewer_system", "separated") == "separated"
            expected = 1.0 if separated else 0.0
            if parameters.get("swds_frac", expected) != expected:
                raise ValueError("sewer_system must match swds_frac (separated=1, mixed=0)")
            if not separated and parameters.get("mss_no_meas_area", 1.0) <= 0:
                raise ValueError("Mixed sewage requires a positive MSS area")
        if self.foul_storage and (not self.uses("sewer") or self.config.get("sewer_system", "separated") != "separated"):
            raise ValueError("Initial foul storage requires a separated foul sewer")
        if self.wwtp_storage and not self.uses("wwtp"):
            raise ValueError("Initial WWTP storage requires wwtp")
        if self.uses("groundwater_infiltration") and parameters.get("gw_no_meas_area", 1.0) <= 0:
            raise ValueError("Groundwater infiltration requires a positive groundwater area")
        if self.uses("wwtp") and self.config.get("wwtp_local_fraction", 0.0) > 0 and parameters.get("ow_no_meas_area", 1.0) <= 0:
            raise ValueError("Local WWTP discharge requires a positive open-water area")

    def uses(self, component):
        return self.enabled and self.config.get(component, False)

    def initial_result(self):
        columns = (
            "dw_import_m3", "dw_leakage_m3", "indoor_use_m3", "garden_use_m3",
            "household_loss_m3", "household_wastewater_m3", "sewer_exfiltration_m3",
            "external_sewage_m3", "external_wwtp_inflow_m3", "gw_sewer_infiltration_m3",
            "sewer_inflow_m3", "groundwater_net_m3", "sewer_to_wwtp_m3",
            "foul_overflow_m3", "foul_storage_m3", "wwtp_local_effluent_m3",
            "wwtp_export_effluent_m3", "wwtp_storage_m3", "cycle_boundary_in_m3",
            "cycle_boundary_out_m3", "cycle_storage_m3",
        )
        result = dict.fromkeys(columns, 0.0)
        result["foul_storage_m3"] = self.foul_storage
        result["wwtp_storage_m3"] = self.wwtp_storage
        result["cycle_storage_m3"] = self.foul_storage + (
            self.wwtp_storage if self.config.get("wwtp_inside_area", False) else 0.0
        )
        return result

    def forcing(self, input_data):
        """Read optional exact-date forcing; inline values take precedence."""
        columns = ("indoor_use_m3", "garden_use_m3", "external_sewage_m3", "external_wwtp_inflow_m3")
        data = input_data.copy()
        if self.config.get("timeseries"):
            extra = pd.read_csv(self.config["timeseries"])
            if "date" not in extra or extra["date"].duplicated().any():
                raise ValueError("Urban water-cycle timeseries requires unique date values")
            extra = extra.set_index("date")
            if not data["date"].isin(extra.index).all():
                raise ValueError("Urban water-cycle timeseries does not cover all forcing dates")
            for column in columns:
                if column in extra and column not in data:
                    data[column] = data["date"].map(extra[column])
        for column in columns:
            if column not in data:
                data[column] = 0.0
            values = pd.to_numeric(data[column], errors="coerce")
            if not values.map(lambda value: math.isfinite(value) and value >= 0).all():
                raise ValueError(f"{column} must contain finite nonnegative m3 per timestep")
            data[column] = values
        for component, fields in (("drinking_water", columns[:2]), ("sewer", (columns[2],)), ("wwtp", (columns[3],))):
            if not self.uses(component) and any(data[field].ne(0).any() for field in fields):
                raise ValueError(f"Nonzero {component} forcing requires that component to be enabled")
        return data

    def prepare(self, forcing, parameters, previous):
        result = self.demand(forcing) if self.uses("drinking_water") else self.demand({})
        result["external_sewage_m3"] = forcing.get("external_sewage_m3", 0.0)
        result["external_wwtp_inflow_m3"] = forcing.get("external_wwtp_inflow_m3", 0.0)
        result["gw_sewer_infiltration_m3"] = 0.0
        if self.uses("groundwater_infiltration"):
            coefficient = previous["sc_gw"]
            head = previous["gwl"] + previous["gwl_sl"] / coefficient
            result["gw_sewer_infiltration_m3"] = self.groundwater_infiltration(
                head, coefficient, parameters["gw_no_meas_area"],
                parameters["delta_t"], parameters.get("gw_bottom", math.inf),
            )
        result["sewer_inflow_m3"] = (
            result["household_wastewater_m3"] - result["sewer_exfiltration_m3"]
            + result["external_sewage_m3"] + result["gw_sewer_infiltration_m3"]
        ) if self.uses("sewer") else 0.0
        result["groundwater_net_m3"] = (
            result["dw_leakage_m3"] + result["sewer_exfiltration_m3"]
            - result["gw_sewer_infiltration_m3"]
        )
        if result["garden_use_m3"] and parameters["up_no_meas_area"] <= 0:
            raise ValueError("Garden watering requires a positive unpaved area")
        if result["garden_use_m3"] and self.config.get("garden_fraction", 1.0) == 0:
            raise ValueError("Garden watering requires a positive garden_fraction")
        if result["groundwater_net_m3"] and parameters["gw_no_meas_area"] <= 0:
            raise ValueError("Pipe leakage requires a positive groundwater area")
        return result

    def route(self, result, sewer, parameters):
        delta_t = parameters["delta_t"]
        to_plant = sewer["q_mss_out"] * parameters["mss_no_meas_area"] / 1000
        overflow = 0.0
        untreated_export = 0.0
        if self.uses("sewer"):
            if self.config.get("sewer_system", "separated") == "separated":
                pumped, overflow = self.foul(result["sewer_inflow_m3"], delta_t)
                to_plant += pumped
        else:
            untreated_export = result["household_wastewater_m3"]
        local = plant_export = 0.0
        inside = self.config.get("wwtp_inside_area", False)
        if self.uses("wwtp"):
            local, plant_export = self.treat(to_plant + result["external_wwtp_inflow_m3"], delta_t)
            boundary_in = result["external_wwtp_inflow_m3"] if inside else local
            boundary_out = plant_export if inside else to_plant
        else:
            boundary_in, boundary_out = 0.0, to_plant
        result.update({
            "sewer_to_wwtp_m3": to_plant,
            "foul_overflow_m3": overflow,
            "foul_storage_m3": self.foul_storage,
            "wwtp_local_effluent_m3": local,
            "wwtp_export_effluent_m3": plant_export,
            "wwtp_storage_m3": self.wwtp_storage,
            "cycle_boundary_in_m3": result["dw_import_m3"] + result["external_sewage_m3"] + boundary_in,
            "cycle_boundary_out_m3": boundary_out + untreated_export + result["household_loss_m3"],
            "cycle_storage_m3": self.foul_storage + (self.wwtp_storage if inside else 0.0),
        })
        if local + overflow > 0 and parameters["ow_no_meas_area"] <= 0:
            raise ValueError("Local effluent or foul overflow requires a positive open-water area")
        return local + overflow

    def demand(self, forcing):
        """Demand is delivered water; leakage is a percentage of network input."""
        indoor = forcing.get("indoor_use_m3", 0.0)
        garden = forcing.get("garden_use_m3", 0.0)
        supplied = indoor + garden
        imported = supplied / (1 - self.config.get("drinking_water_loss_percent", 0.0) / 100)
        wastewater = indoor * self.config.get("indoor_return_fraction", 1.0)
        leakage = wastewater * self.config.get("sewer_loss_percent", 0.0) / 100 if self.uses("sewer") else 0.0
        return {
            "dw_import_m3": imported,
            "dw_leakage_m3": imported - supplied,
            "indoor_use_m3": indoor,
            "garden_use_m3": garden,
            "household_loss_m3": indoor - wastewater,
            "household_wastewater_m3": wastewater,
            "sewer_exfiltration_m3": leakage,
        }

    def foul(self, inflow, delta_t):
        available = self.foul_storage + inflow
        pumped = min(available, self.config.get("foul_capacity_m3_day", math.inf) * delta_t)
        overflow = max(0.0, available - pumped - self.config.get("foul_storage_capacity_m3", math.inf))
        self.foul_storage = available - pumped - overflow
        return pumped, overflow

    def groundwater_infiltration(self, head, storage_coefficient, area, delta_t, bottom=math.inf):
        """Drain only pre-step groundwater above the sewer level, without sewer heads."""
        depth = min(self.config["sewer_depth_m"], bottom)
        excess_head = max(0.0, depth - head)
        resistance = self.config["sewer_entry_resistance_days"]
        depth_mm = 1000 * storage_coefficient * excess_head * -math.expm1(
            -delta_t / (resistance * storage_coefficient)
        )
        return depth_mm * area / 1000

    def treat(self, inflow, delta_t):
        available = self.wwtp_storage + inflow
        residence = self.config.get("wwtp_residence_days", 0.0)
        released = available if residence == 0 else available * -math.expm1(-delta_t / residence)
        released = min(released, self.config.get("wwtp_capacity_m3_day", math.inf) * delta_t)
        self.wwtp_storage = available - released
        local = released * self.config.get("wwtp_local_fraction", 0.0)
        return local, released - local