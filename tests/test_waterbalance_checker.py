"""Tests for the groundwater storage term in the water balance checker.

The groundwater storage change is computed from the net groundwater flux
(percolation + measure inflow - deep seepage - drainage to open water) rather
than the level-based ``sc * dgwl`` form. This keeps the water balance closed
even when the groundwater ponds above the surface (``gwl_sl != 0``), which the
level-based form does not.
"""

import pandas as pd
import pytest

import urbanwb
from urbanwb.waterbalance_checker import water_balance_checker

# Columns read by water_balance_checker for the entire-model balance.
_ZERO_COLUMNS = [
    "P_atm",
    "e_atm_pr",
    "e_atm_cp",
    "e_atm_op",
    "e_atm_up",
    "t_atm_uz",
    "e_atm_ow",
    "e_atm_meas",
    "t_atm_top_meas",
    "t_atm_btm_meas",
    "q_ow_out",
    "q_meas_out",
    "q_mss_out",
    "s_gw_out",
    "intstor_pr",
    "intstor_cp",
    "intstor_op",
    "fin_intstor_up",
    "theta_uz",
    "sum_p_gw",
    "r_meas_gw",
    "d_gw_ow",
    "stor_swds",
    "stor_mss",
    "owl",
    "intstor_meas",
    "fin_stor_top_meas",
    "fin_stor_btm_meas",
    "prec_meas",
    "sum_r_meas",
    "q_meas_gw",
    "q_meas_ow",
    "q_meas_swds",
    "q_meas_mss",
]

_ZERO_PARAMS = {
    "tot_area": 1.0,
    "tot_meas_area": 0.0,
    "top_meas_area": 0.0,
    "btm_meas_area": 0.0,
    "ow_no_meas_area": 0.0,
    "tot_mss_area": 0.0,
    "gw_no_meas_area": 1.0,
    "swds_no_meas_area": 0.0,
    "mss_no_meas_area": 0.0,
    "pr_no_meas_area": 0.0,
    "cp_no_meas_area": 0.0,
    "op_no_meas_area": 0.0,
    "up_no_meas_area": 0.0,
    "uz_no_meas_area": 0.0,
    "tot_meas_inflow_area": 0.0,
    "pr_meas_inflow_area": 0.0,
    "pr_meas_area": 0.0,
    "cp_meas_inflow_area": 0.0,
    "cp_meas_area": 0.0,
    "op_meas_inflow_area": 0.0,
    "op_meas_area": 0.0,
    "up_meas_inflow_area": 0.0,
    "up_meas_area": 0.0,
    "ow_meas_inflow_area": 0.0,
    "ow_meas_area": 0.0,
}


def test_groundwater_storage_is_flux_based_and_closes_with_ponding():
    """Rain routed entirely into groundwater closes the balance via net fluxes.

    ``gwl_sl`` (above-surface ponding) is set to a large value to prove it is NOT
    used by the balance: the flux-based storage change already accounts for it.
    The level-based form would add a spurious ~5000 mm term and fail to close.
    """
    n = 4
    df = pd.DataFrame({col: [0.0] * n for col in _ZERO_COLUMNS})
    # Rain over the whole area, all of it recharging groundwater (no losses).
    df["P_atm"] = [0.0, 10.0, 10.0, 10.0]
    df["sum_p_gw"] = [0.0, 10.0, 10.0, 10.0]
    # Groundwater ponds above the surface; must be ignored by the flux-based term.
    df["gwl"] = [0.0, 0.0, 0.0, 0.0]
    df["gwl_sl"] = [0.0, 0.0, 0.0, -5.0]

    stat_model, _, _, warnings = water_balance_checker(df, dict(_ZERO_PARAMS), n)

    assert stat_model["balance diff"] == pytest.approx(0.0, abs=1e-9)
    # All 30 mm of rain ended up as groundwater storage.
    assert stat_model["storage diff"] == pytest.approx(30.0)
    assert warnings == []


def test_groundwater_storage_accounts_for_seepage():
    """Deep seepage reduces the groundwater storage term and stays balanced."""
    n = 3
    df = pd.DataFrame({col: [0.0] * n for col in _ZERO_COLUMNS})
    df["P_atm"] = [0.0, 20.0, 20.0]
    df["sum_p_gw"] = [0.0, 20.0, 20.0]
    df["s_gw_out"] = [0.0, 5.0, 5.0]  # to deep groundwater (external outflow)

    stat_model, _, _, warnings = water_balance_checker(df, dict(_ZERO_PARAMS), n)

    # Rain 40, deep seepage 10 -> groundwater storage increase 30.
    assert stat_model["balance diff"] == pytest.approx(0.0, abs=1e-9)
    assert stat_model["storage diff"] == pytest.approx(30.0)
    assert warnings == []


def test_open_water_storage_sign_closes_when_level_drifts():
    """Open water discharging to outside lowers its storage; balance stays closed.

    ``owl`` is in m-SL, so storage rises as ``owl`` falls. This exercises the sign
    of the open-water storage term, which a target-controlled (cap) run leaves
    near zero but a drifting level (e.g. with a Q(h) relation) exposes.
    """
    n = 3
    df = pd.DataFrame({col: [0.0] * n for col in _ZERO_COLUMNS})
    df["P_atm"] = [0.0, 10.0, 10.0]  # rain 20 mm
    df["q_ow_out"] = [0.0, 4.0, 4.0]  # discharge 8 mm to outside water
    df["owl"] = [1.0, 0.994, 0.988]  # level rises (m-SL falls) -> storage +12 mm

    params = dict(_ZERO_PARAMS)
    params["gw_no_meas_area"] = 0.0
    params["ow_no_meas_area"] = 1.0

    stat_model, _, _, warnings = water_balance_checker(df, params, n)
    assert stat_model["balance diff"] == pytest.approx(0.0, abs=1e-9)
    assert stat_model["storage diff"] == pytest.approx(12.0)
    assert warnings == []


def test_short_model_run_balance_closes():
    """End-to-end: a short run on the example forcing keeps the balance closed."""
    from urbanwb.main import read_parameters, running

    example = urbanwb.urbanwbdir / ".." / "examples" / "input"
    dict_param = read_parameters(
        str(example / "ep_neighbourhood.ini"), str(example / "ep_measure.ini")
    )
    ts = pd.read_csv(example / "ep_ts.csv").iloc[:1500].reset_index(drop=True)

    _, wbc = running(ts, dict_param)
    stat_model = wbc[0]

    assert stat_model["balance diff"] == pytest.approx(0.0, abs=1e-6)


def test_coupled_bottoms_limit_all_donor_fluxes():
    """A dry coupled run cannot drain either store through its internal fluxes."""
    from urbanwb.main import read_parameters, running

    example = urbanwb.urbanwbdir / ".." / "examples" / "input"
    dict_param = read_parameters(
        str(example / "ep_neighbourhood.ini"), str(example / "ep_measure.ini")
    )
    bottom = 1.1
    dict_param.update(
        gw_bottom=bottom,
        ow_bottom=bottom,
        q_ow_in_cap=0.0,
    )
    ts = pd.read_csv(example / "ep_ts.csv").iloc[:30000].reset_index(drop=True)

    results, wbc = running(ts, dict_param)
    df = pd.DataFrame(results)

    assert df["gwl"].max() <= bottom
    assert df["h_gw"].max() <= bottom
    assert df["owl"].max() <= bottom
    assert wbc[0]["balance diff"] == pytest.approx(0.0, abs=1e-6)
