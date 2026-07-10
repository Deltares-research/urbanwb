import pytest

from urbanwb.measure import Measure


def _measure_kwargs(**overrides):
    """Full set of Measure constructor arguments with sensible, inert defaults.

    Defaults are chosen so that only the bottom storage layer is active: no
    evaporation/transpiration, no percolation to groundwater, a two-level measure
    with an initial bottom storage that both discharges (controlled runoff) and
    overflows on the first time step.
    """
    kwargs = dict(
        tot_meas_area=1000.0,
        runoff_to_stor_layer=1,
        intstor_meas_t0=0.0,
        EV_evaporation=0,
        num_stor_lvl=2,
        infilcap_int_meas=0.0,
        storcap_top_meas=0.0,
        storcap_btm_meas=50.0,
        stor_top_meas_t0=0.0,
        stor_btm_meas_t0=100.0,
        storcap_int_meas=0.0,
        top_meas_area=0.0,
        ET_transpiration=0,
        evaporation_factor_meas=0.0,
        IN_infiltration=0,
        infilcap_top_meas=0.0,
        btm_meas_area=400.0,
        btm_meas_transpiration=0,
        connection_to_gw=0,
        limited_by_gwl=0,
        k_sat_uz=0.0,
        btm_level_meas=0.6858,
        btm_discharge_type=0,
        runoffcap_btm_meas=240.0,
        dischlvl_btm_meas=0.0,
        c_btm_meas=0.0,
        surf_runoff_meas_OW=0,
        ctrl_runoff_meas_OW=0,
        overflow_meas_OW=0,
        surf_runoff_meas_UZ=0,
        ctrl_runoff_meas_UZ=0,
        overflow_meas_UZ=0,
        surf_runoff_meas_GW=0,
        ctrl_runoff_meas_GW=0,
        overflow_meas_GW=0,
        surf_runoff_meas_SWDS=0,
        ctrl_runoff_meas_SWDS=0,
        overflow_meas_SWDS=0,
        surf_runoff_meas_MSS=0,
        ctrl_runoff_meas_MSS=0,
        overflow_meas_MSS=0,
        surf_runoff_meas_Out=0,
        ctrl_runoff_meas_Out=0,
        overflow_meas_Out=0,
        greenroof_type_measure=0,
    )
    kwargs.update(overrides)
    return kwargs


def _measure_sol(m):
    """Run one time step with no external inflow (dry, area-only bottom dynamics)."""
    return m.sol(
        p_atm=0.0,
        e_pot_ow=0.0,
        r_pr_meas=0.0,
        r_cp_meas=0.0,
        r_op_meas=0.0,
        r_up_meas=0.0,
        pr_no_meas_area=0.0,
        cp_no_meas_area=0.0,
        op_no_meas_area=0.0,
        up_no_meas_area=0.0,
        gw_no_meas_area=0.0,
        gwl_prevt=1.0,
        delta_t=1 / 24,
    )


def test_measure_bottom_layer_produces_runoff_and_overflow():
    """Sanity: the default setup yields both controlled runoff and overflow."""
    res = _measure_sol(
        Measure(**_measure_kwargs(ctrl_runoff_meas_OW=1, overflow_meas_OW=1))
    )
    # runoff_btm = min(240/24, 100) = 10 ; overflow_btm = 100 - 10 - 50 = 40
    assert res["runoff_btm_meas"] == pytest.approx(10.0)
    assert res["overflow_btm_meas"] == pytest.approx(40.0)


def test_measure_bottom_flux_scaled_by_btm_over_tot():
    """Bottom-layer contribution to a measure outflow is scaled by btm/tot area."""
    tot, btm = 1000.0, 400.0
    m = Measure(
        **_measure_kwargs(
            tot_meas_area=tot,
            btm_meas_area=btm,
            ctrl_runoff_meas_OW=1,
            overflow_meas_OW=1,
        )
    )
    res = _measure_sol(m)
    expected = (res["runoff_btm_meas"] + res["overflow_btm_meas"]) * btm / tot
    assert res["q_meas_ow"] == pytest.approx(expected)
    assert res["q_meas_ow"] == pytest.approx(50.0 * 0.4)  # 20.0
    # Guard against the previous (inverted) tot/btm scaling.
    inverted = (res["runoff_btm_meas"] + res["overflow_btm_meas"]) * tot / btm
    assert res["q_meas_ow"] != pytest.approx(inverted)


def test_measure_bottom_flux_scales_linearly_with_btm_area():
    """Halving the bottom area halves the bottom-layer contribution (mass conserving)."""
    full = _measure_sol(
        Measure(
            **_measure_kwargs(
                tot_meas_area=1000.0,
                btm_meas_area=1000.0,
                ctrl_runoff_meas_OW=1,
                overflow_meas_OW=1,
            )
        )
    )
    half = _measure_sol(
        Measure(
            **_measure_kwargs(
                tot_meas_area=1000.0,
                btm_meas_area=500.0,
                ctrl_runoff_meas_OW=1,
                overflow_meas_OW=1,
            )
        )
    )
    # Bottom-layer dynamics (per-area depths) are identical; only the area ratio differs.
    assert half["runoff_btm_meas"] == pytest.approx(full["runoff_btm_meas"])
    assert half["overflow_btm_meas"] == pytest.approx(full["overflow_btm_meas"])
    assert half["q_meas_ow"] == pytest.approx(0.5 * full["q_meas_ow"])


def test_measure_bottom_flux_routes_to_distinct_destinations():
    """Controlled runoff and overflow can be routed independently, each area-scaled."""
    tot, btm = 1000.0, 400.0
    m = Measure(
        **_measure_kwargs(
            tot_meas_area=tot,
            btm_meas_area=btm,
            ctrl_runoff_meas_OW=1,  # controlled runoff -> open water
            overflow_meas_GW=1,  # overflow -> groundwater
        )
    )
    res = _measure_sol(m)
    assert res["q_meas_ow"] == pytest.approx(res["runoff_btm_meas"] * btm / tot)
    assert res["q_meas_gw"] == pytest.approx(res["overflow_btm_meas"] * btm / tot)
