import pytest

from urbanwb.watercycle import WaterCycle


@pytest.mark.parametrize("fraction", [-0.1, 1.1, float("nan"), "0.1", True])
def test_invalid_garden_fraction_is_rejected(fraction):
    with pytest.raises(ValueError, match="garden_fraction"):
        WaterCycle({"urban_water_cycle": {"enabled": True, "garden_fraction": fraction}})


def test_zero_garden_fraction_rejects_watering():
    cycle = WaterCycle({"urban_water_cycle": {
        "enabled": True, "drinking_water": True, "garden_fraction": 0,
    }})
    with pytest.raises(ValueError, match="positive garden_fraction"):
        cycle.prepare({"garden_use_m3": 1}, {"up_no_meas_area": 1000}, {})


def test_garden_split_preserves_volume_and_independent_moisture():
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {
        "enabled": True, "drinking_water": True, "garden_fraction": 0.1,
    }
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:25].copy()
    forcing[["P_atm", "Ref.grass", "E_pot_OW"]] = 0.0
    forcing["garden_use_m3"] = 0.0
    forcing.loc[1, "garden_use_m3"] = 20.0
    results, balances = running(forcing, parameters)
    expected = 20000 / (0.1 * parameters["up_no_meas_area"])
    assert results["garden_init_intstor_up"].iloc[1] == pytest.approx(expected)
    assert results["other_unpaved_init_intstor_up"].iloc[1] == 0
    assert results["garden_theta_uz"].iloc[2] > results["other_unpaved_theta_uz"].iloc[2]
    for column in ("fin_intstor_up", "e_atm_up", "r_up_ow", "theta_uz", "p_uz_gw", "t_atm_uz"):
        weighted = 0.1 * results[f"garden_{column}"] + 0.9 * results[f"other_unpaved_{column}"]
        assert results[column].iloc[1:].to_numpy() == pytest.approx(weighted.iloc[1:].to_numpy())
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_supply_loss_and_household_split():
    cycle = WaterCycle({"urban_water_cycle": {
        "enabled": True, "drinking_water": True, "sewer": True,
        "drinking_water_loss_percent": 20, "indoor_return_fraction": 0.9,
        "sewer_loss_percent": 10,
    }})
    result = cycle.demand({"indoor_use_m3": 80, "garden_use_m3": 20})
    assert result["dw_import_m3"] == pytest.approx(125)
    assert result["dw_leakage_m3"] == pytest.approx(25)
    assert result["household_wastewater_m3"] == pytest.approx(72)
    assert result["household_loss_m3"] == pytest.approx(8)
    assert result["sewer_exfiltration_m3"] == pytest.approx(7.2)


def test_optional_components_and_storage_conservation():
    assert not WaterCycle({}).uses("sewer")
    cycle = WaterCycle({"urban_water_cycle": {
        "enabled": True, "foul_capacity_m3_day": 24,
        "foul_storage_capacity_m3": 2, "wwtp_residence_days": 1,
        "wwtp_local_fraction": 0.4,
    }})
    pumped, overflow = cycle.foul(10, 1 / 24)
    assert (pumped, overflow, cycle.foul_storage) == pytest.approx((1, 7, 2))
    local, exported = cycle.treat(pumped, 1 / 24)
    assert local + exported + cycle.wwtp_storage == pytest.approx(pumped)
    assert local / (local + exported) == pytest.approx(0.4)


def test_groundwater_drainage_is_one_way_and_storage_limited():
    cycle = WaterCycle({"urban_water_cycle": {
        "enabled": True, "sewer": True, "groundwater_infiltration": True,
        "sewer_depth_m": 2, "sewer_entry_resistance_days": 10,
    }})
    assert cycle.groundwater_infiltration(3, 0.2, 1000, 1) == 0
    volume = cycle.groundwater_infiltration(1, 0.2, 1000, 1)
    assert 0 < volume < 200
    assert cycle.groundwater_infiltration(1, 0.2, 1000, 10000) == pytest.approx(200)
    assert cycle.groundwater_infiltration(1, 0.2, 1000, 10000, bottom=1.5) == pytest.approx(100)


@pytest.mark.parametrize("system", ["separated", "mixed"])
@pytest.mark.parametrize("inside", [True, False])
def test_full_cycle_closes_project_balance(system, inside):
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    if system == "mixed":
        area = parameters["swds_no_meas_area"]
        parameters.update(swds_frac=0, swds_no_meas_area=0, mss_no_meas_area=area, tot_swds_area=0, tot_mss_area=area)
    parameters["urban_water_cycle"] = {
        "enabled": True, "drinking_water": True, "sewer": True,
        "groundwater_infiltration": True, "wwtp": True,
        "sewer_system": system, "drinking_water_loss_percent": 10,
        "garden_fraction": 0.1,
        "indoor_return_fraction": 0.95, "sewer_loss_percent": 2,
        "sewer_depth_m": 2, "sewer_entry_resistance_days": 100,
        "wwtp_inside_area": inside, "wwtp_local_fraction": 0.7,
        "wwtp_residence_days": 0.2,
        "foul_capacity_m3_day": 200, "foul_storage_capacity_m3": 10,
    }
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:73].copy()
    forcing["indoor_use_m3"] = 2.0
    forcing["garden_use_m3"] = 0.5
    forcing["external_sewage_m3"] = 1.0
    forcing["external_wwtp_inflow_m3"] = 4.0
    results, balances = running(forcing, parameters)
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)
    assert results["gw_sewer_infiltration_m3"].iloc[1:].gt(0).all()
    assert results["wwtp_local_effluent_m3"].iloc[1:].gt(0).all()


def test_example_runs_and_disabled_cycle_is_unchanged():
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    weather = pd.read_csv("examples/input/ep_ts.csv").iloc[:25]
    disabled, _ = running(weather, parameters)
    legacy_parameters = dict(parameters)
    legacy_parameters.pop("urban_water_cycle")
    legacy, _ = running(weather, legacy_parameters)
    pd.testing.assert_frame_equal(disabled, legacy)
    parameters["urban_water_cycle"]["enabled"] = True
    forcing = pd.read_csv("examples/input/ep_water_cycle_ts.csv")
    results, balances = running(forcing, parameters)
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)
    assert results["dw_import_m3"].sum() > forcing["indoor_use_m3"].sum()
    assert results["wwtp_storage_m3"].iloc[-1] > 0


@pytest.mark.parametrize("drinking,sewer,wwtp", [
    (False, False, False), (True, False, False), (False, True, False),
    (False, False, True), (True, True, False), (True, False, True),
    (False, True, True), (True, True, True),
])
def test_components_can_be_enabled_independently(drinking, sewer, wwtp):
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {
        "enabled": True, "drinking_water": drinking, "sewer": sewer,
        "wwtp": wwtp, "wwtp_inside_area": True, "wwtp_local_fraction": 0.5,
    }
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:25].copy()
    if drinking:
        forcing["indoor_use_m3"] = 2
        forcing["garden_use_m3"] = 1
    if sewer:
        forcing["external_sewage_m3"] = 3
    if wwtp:
        forcing["external_wwtp_inflow_m3"] = 4
    results, balances = running(forcing, parameters)
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)
    if not sewer:
        assert results["sewer_inflow_m3"].eq(0).all()


@pytest.mark.parametrize("inside", [True, False])
def test_initial_storage_and_foul_overflow_are_conserved(inside):
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {
        "enabled": True, "sewer": True, "wwtp": True,
        "foul_initial_storage_m3": 5, "foul_storage_capacity_m3": 5,
        "foul_capacity_m3_day": 24, "wwtp_initial_storage_m3": 10,
        "wwtp_residence_days": 1, "wwtp_capacity_m3_day": 48,
        "wwtp_local_fraction": 0.5, "wwtp_inside_area": inside,
    }
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:25].copy()
    forcing["external_sewage_m3"] = 3
    results, balances = running(forcing, parameters)
    assert results["cycle_storage_m3"].iloc[0] == (15 if inside else 5)
    assert results["foul_overflow_m3"].iloc[1:].eq(2).all()
    assert results["sewer_to_wwtp_m3"].iloc[1:].eq(1).all()
    assert results["cycle_boundary_in_m3"].iloc[0] == 0
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("options", [
    {"enabled": "false"}, {"drinking_water_loss_percent": 100},
    {"drinking_water_loss_percent": -1}, {"indoor_return_fraction": 1.1},
    {"sewer_loss_percent": 1}, {"sewer": "true"},
    {"wwtp_local_fraction": float("nan")}, {"wwtp_capacity_m3_day": float("inf")},
    {"foul_capacity_m3_day": "10"}, {"unknown_option": 1},
    {"groundwater_infiltration": True},
    {"sewer": True, "groundwater_infiltration": True, "sewer_depth_m": 2, "sewer_entry_resistance_days": 0},
    {"sewer_system": "other"}, {"wwtp_initial_storage_m3": 1},
    {"sewer": True, "foul_storage_capacity_m3": 1, "foul_initial_storage_m3": 2},
])
def test_invalid_configuration_is_rejected(options):
    with pytest.raises(ValueError):
        WaterCycle({"urban_water_cycle": {"enabled": True, **options}})


@pytest.mark.parametrize("value", [-1, float("inf"), float("nan"), "bad"])
def test_invalid_forcing_is_rejected(value):
    import pandas as pd

    cycle = WaterCycle({"urban_water_cycle": {"enabled": True, "drinking_water": True}})
    with pytest.raises(ValueError, match="finite nonnegative"):
        cycle.forcing(pd.DataFrame({"date": ["start"], "indoor_use_m3": [value]}))


def test_disabled_component_rejects_nonzero_forcing():
    import pandas as pd

    cycle = WaterCycle({"urban_water_cycle": {"enabled": True}})
    with pytest.raises(ValueError, match="requires that component"):
        cycle.forcing(pd.DataFrame({"date": ["start"], "indoor_use_m3": [1]}))


def test_separate_timeseries_alignment_and_inline_override(tmp_path):
    import pandas as pd

    path = tmp_path / "cycle.csv"
    pd.DataFrame({"date": ["second", "first"], "indoor_use_m3": [2, 1]}).to_csv(path, index=False)
    cycle = WaterCycle({"urban_water_cycle": {
        "enabled": True, "drinking_water": True, "timeseries": str(path),
    }})
    weather = pd.DataFrame({"date": ["first", "second"]})
    assert cycle.forcing(weather)["indoor_use_m3"].tolist() == [1, 2]
    weather["indoor_use_m3"] = 3
    assert cycle.forcing(weather)["indoor_use_m3"].tolist() == [3, 3]
    with pytest.raises(ValueError, match="cover all"):
        cycle.forcing(pd.DataFrame({"date": ["missing"]}))
    pd.DataFrame({"date": ["first", "first"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="unique date"):
        cycle.forcing(weather)


def test_missing_receiver_areas_are_rejected():
    cycle = WaterCycle({"urban_water_cycle": {"enabled": True, "drinking_water": True}})
    with pytest.raises(ValueError, match="unpaved area"):
        cycle.prepare({"garden_use_m3": 1}, {"up_no_meas_area": 0}, {})
    with pytest.raises(ValueError, match="open-water area"):
        WaterCycle({"urban_water_cycle": {"enabled": True, "wwtp": True, "wwtp_local_fraction": 1}, "ow_no_meas_area": 0})
    with pytest.raises(ValueError, match="match swds_frac"):
        WaterCycle({"urban_water_cycle": {"enabled": True, "sewer": True, "sewer_system": "mixed"}, "swds_frac": 1})


def test_wwtp_and_groundwater_drainage_respect_timestep():
    parameters = {"urban_water_cycle": {
        "enabled": True, "wwtp": True, "wwtp_initial_storage_m3": 100,
        "wwtp_residence_days": 1, "wwtp_local_fraction": 1,
        "sewer": True, "groundwater_infiltration": True,
        "sewer_depth_m": 2, "sewer_entry_resistance_days": 10,
    }}
    daily = WaterCycle(parameters)
    hourly = WaterCycle(parameters)
    local, _ = daily.treat(0, 1)
    hourly_local = sum(hourly.treat(0, 1 / 24)[0] for _ in range(24))
    assert hourly_local == pytest.approx(local)
    daily_infiltration = daily.groundwater_infiltration(1, 0.2, 1000, 1)
    head = 1
    total = 0
    for _ in range(24):
        drained = hourly.groundwater_infiltration(head, 0.2, 1000, 1 / 24)
        total += drained
        head += drained / (0.2 * 1000)
    assert total == pytest.approx(daily_infiltration)


def test_garden_water_enters_surface_storage_not_precipitation():
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {"enabled": True, "drinking_water": True}
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:2].copy()
    forcing["garden_use_m3"] = [0, 20]
    results, balances = running(forcing, parameters)
    assert results["P_atm"].eq(0).all()
    assert results["init_intstor_up"].iloc[1] == pytest.approx(20000 / parameters["up_no_meas_area"])
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("resistance", [0.000001, 0.1, 100])
def test_sewer_drainage_respects_coupled_finite_bottoms(resistance):
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters.update(gw_bottom=1.1, ow_bottom=1.1, q_ow_in_cap=0.0)
    parameters["urban_water_cycle"] = {
        "enabled": True, "sewer": True, "groundwater_infiltration": True,
        "sewer_depth_m": 2, "sewer_entry_resistance_days": resistance,
    }
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:241].copy()
    forcing["P_atm"] = 0.0
    results, balances = running(forcing, parameters)
    assert results["gwl"].max() <= 1.1
    assert results["owl"].max() <= 1.1
    assert results["gw_sewer_infiltration_m3"].ge(0).all()
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_drinking_water_leakage_increases_groundwater_storage():
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {"enabled": True, "drinking_water": True}
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:2].copy()
    forcing["indoor_use_m3"] = [0, 4]
    baseline, _ = running(forcing, parameters)
    parameters["urban_water_cycle"]["drinking_water_loss_percent"] = 20
    leaky, balances = running(forcing, parameters)
    assert leaky["dw_leakage_m3"].iloc[1] == pytest.approx(1)
    assert leaky["sum_p_gw"].iloc[1] - baseline["sum_p_gw"].iloc[1] == pytest.approx(1000 / parameters["gw_no_meas_area"])
    assert leaky["gwl"].iloc[1] < baseline["gwl"].iloc[1]
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_mixed_sewer_pump_override_uses_volume_per_day():
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    area = parameters["swds_no_meas_area"]
    parameters.update(swds_frac=0, swds_no_meas_area=0, mss_no_meas_area=area, tot_swds_area=0, tot_mss_area=area)
    parameters["urban_water_cycle"] = {
        "enabled": True, "sewer": True, "sewer_system": "mixed",
        "mixed_capacity_m3_day": 24,
    }
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:2].copy()
    forcing["external_sewage_m3"] = [0, 10]
    results, balances = running(forcing, parameters)
    assert results["sewer_to_wwtp_m3"].iloc[1] == pytest.approx(1)
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_default_garden_fraction_matches_single_area_solver(monkeypatch):
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {"enabled": True, "drinking_water": True}
    forcing = pd.read_csv("examples/input/ep_water_cycle_ts.csv")
    forcing = forcing.drop(columns=["external_wwtp_inflow_m3", "external_sewage_m3"])
    default, balances = running(forcing, parameters)
    parameters["urban_water_cycle"]["garden_fraction"] = 1.0
    explicit, _ = running(forcing, parameters)
    pd.testing.assert_frame_equal(default, explicit)
    monkeypatch.setattr("urbanwb.main.UnpavedAreas", lambda *args: None)
    original, _ = running(forcing, parameters)
    pd.testing.assert_frame_equal(default[original.columns], original, check_dtype=False, check_exact=True)
    assert default["other_unpaved_area_m2"].eq(0).all()
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("fraction", [0.0, 0.1, 0.5])
def test_garden_split_without_irrigation_preserves_aggregate_results(fraction):
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {"enabled": True, "drinking_water": True}
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:241]
    original, _ = running(forcing, parameters)
    parameters["urban_water_cycle"]["garden_fraction"] = fraction
    split, balances = running(forcing, parameters)
    columns = [column for column in original if not column.startswith(("garden_", "other_unpaved_"))]
    pd.testing.assert_frame_equal(split[columns], original[columns], check_dtype=False, rtol=1e-10, atol=1e-10)
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_concentrated_irrigation_increases_runoff_without_creating_water():
    import pandas as pd

    from urbanwb.main import read_parameters, running

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {"enabled": True, "drinking_water": True}
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:3].copy()
    forcing["garden_use_m3"] = [0.0, 2000.0, 0.0]
    entire_area, _ = running(forcing, parameters)
    parameters["urban_water_cycle"]["garden_fraction"] = 0.1
    garden, balances = running(forcing, parameters)
    assert garden["r_up_ow"].iloc[1] > entire_area["r_up_ow"].iloc[1]
    assert garden["i_up_uz"].iloc[1] < entire_area["i_up_uz"].iloc[1]
    assert garden["dw_import_m3"].sum() == entire_area["dw_import_m3"].sum()
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_split_capillary_limit_only_reduces_requesting_rootzones():
    from urbanwb.main import UrbanwbModel, read_parameters

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["urban_water_cycle"] = {
        "enabled": True, "drinking_water": True, "garden_fraction": 0.1,
    }
    areas = UrbanwbModel(parameters).unpaved_areas
    areas.root_solutions = {
        "garden": {"p_uz_gw": 2.0, "theta_uz": 100.0},
        "other_unpaved": {"p_uz_gw": -3.0, "theta_uz": 100.0},
    }
    aggregate = {"p_uz_gw": -2.5, "theta_uz": 100.0}
    areas.limit_capillary_rise(aggregate, -1.0)
    assert areas.root_solutions["garden"] == {"p_uz_gw": 2.0, "theta_uz": 100.0}
    assert areas.root_solutions["other_unpaved"]["p_uz_gw"] == pytest.approx(-4 / 3)
    assert aggregate["theta_uz"] == pytest.approx(98.5)
    areas.limit_capillary_rise(aggregate, 0.0)
    assert aggregate["theta_uz"] == pytest.approx(97.5)
    assert areas.root_solutions["other_unpaved"]["p_uz_gw"] <= 0
    assert areas.rootzones["other_unpaved"].theta_uz_prevt == areas.diagnostics()["other_unpaved_theta_uz"]
    with pytest.raises(ValueError, match="requested groundwater supply"):
        areas.limit_capillary_rise(aggregate, 1.0)


def test_split_gardens_preserve_balance_at_finite_storage_bottoms(monkeypatch):
    import pandas as pd

    from urbanwb.main import read_parameters, running
    from urbanwb.unpaved import UnpavedAreas

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters.update(gw_bottom=1.03, ow_bottom=1.03, q_ow_in_cap=0.0)
    parameters["urban_water_cycle"] = {
        "enabled": True, "drinking_water": True, "garden_fraction": 0.1,
    }
    corrections = []
    original = UnpavedAreas.limit_capillary_rise

    def record_limit(self, solution, p_uz_gw):
        corrections.append(p_uz_gw - solution["p_uz_gw"])
        return original(self, solution, p_uz_gw)

    monkeypatch.setattr(UnpavedAreas, "limit_capillary_rise", record_limit)
    forcing = pd.read_csv("examples/input/ep_ts.csv").iloc[:241].copy()
    forcing["P_atm"] = 0.0
    forcing["Ref.grass"] = 0.2
    forcing["E_pot_OW"] = 0.1
    forcing["garden_use_m3"] = 0.0
    forcing.loc[10, "garden_use_m3"] = 200.0
    results, balances = running(forcing, parameters)
    assert corrections and max(corrections) > 0
    assert results["gwl"].max() <= 1.03
    assert results["owl"].max() <= 1.03
    assert results["theta_uz"].iloc[1:].to_numpy() == pytest.approx(
        (0.1 * results["garden_theta_uz"] + 0.9 * results["other_unpaved_theta_uz"]).iloc[1:].to_numpy()
    )
    assert balances[0]["balance diff"] == pytest.approx(0, abs=1e-6)


def test_garden_areas_distribute_paved_runoff_and_measure_inflow_uniformly():
    from urbanwb.main import UrbanwbModel, read_parameters

    parameters = read_parameters("examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini")
    parameters["up_no_meas_area"] -= 1000
    parameters["uz_no_meas_area"] -= 1000
    parameters.update(up_meas_area=1000, up_meas_inflow_area=2000)
    parameters["urban_water_cycle"] = {
        "enabled": True, "drinking_water": True, "garden_fraction": 0.2,
    }
    areas = UrbanwbModel(parameters).unpaved_areas
    surface = areas.surface_sol(
        p_atm=0.5, e_pot_ow=0, r_pr_up=1, r_cp_up=2, r_op_up=3,
        theta_uz_prevt=0, pr_no_meas_area=parameters["pr_no_meas_area"],
        cp_no_meas_area=parameters["cp_no_meas_area"],
        op_no_meas_area=parameters["op_no_meas_area"],
        ow_no_meas_area=parameters["ow_no_meas_area"],
        delta_t=parameters["delta_t"], irrigation=0,
    )
    expected_runoff = (
        parameters["pr_no_meas_area"] + 2 * parameters["cp_no_meas_area"]
        + 3 * parameters["op_no_meas_area"]
    ) / parameters["up_no_meas_area"]
    for name, fraction in areas.fractions.items():
        assert areas.surface_solutions[name]["sum_r_up"] == pytest.approx(expected_runoff)
        assert areas.surfaces[name].up_no_meas_area == pytest.approx(fraction * parameters["up_no_meas_area"])
        assert areas.surfaces[name].up_meas_area == pytest.approx(fraction * 1000)
    roots = areas.sol(
        i_up_uz=surface["i_up_uz"], meas_uz=2, e_ref=0,
        tot_meas_area=parameters["tot_meas_area"], gwl_prevt=parameters["gwl_t0"],
        delta_t=parameters["delta_t"],
    )
    expected_measure_inflow = 2 * parameters["tot_meas_area"] / parameters["uz_no_meas_area"]
    assert roots["r_meas_uz"] == pytest.approx(expected_measure_inflow)
    for result in areas.root_solutions.values():
        assert result["r_meas_uz"] == pytest.approx(expected_measure_inflow)