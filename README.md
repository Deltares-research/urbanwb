# Urban water balance model

The `urbanwb` model is a lumped conceptual multi-reservoir hydrological model that quickly
simulates dominant hydrological processes of an urban water system. 

The main documentation can be found at
https://publicwiki.deltares.nl/display/AST/Urban+Water+balance+model.

This model was proposed by Toine Vergroesen (Deltares) in 2012. Wenxing Zhang converted the
original Excel version into this Python module.

To install the package, please do "pip install -e ." with cmd in the package root directory.

The model is available under the MIT license.

## Optional urban water cycle

The neighbourhood TOML file can contain an `[urban_water_cycle]` table.
Omitting it, or setting `enabled = false`, preserves existing simulations and
output columns. The example neighbourhood includes all settings with the master
switch off. Enable only the components needed: `drinking_water`, `sewer`,
`groundwater_infiltration`, and `wwtp`.

### Run the example

From the repository root:

```python
import pandas as pd
from urbanwb.main import read_parameters, running

parameters = read_parameters(
		"examples/input/ep_neighbourhood.ini", "examples/input/ep_measure.ini"
)
parameters["urban_water_cycle"]["enabled"] = True
forcing = pd.read_csv("examples/input/ep_water_cycle_ts.csv")
results, balances = running(forcing, parameters)
```

The example contains one initialization row followed by 24 hourly steps. Its
weather is from the existing example; demand, irrigation, outside-area wastewater,
and infrastructure parameters are illustrative, not calibrated observations.

### Dynamic inputs

Add these optional columns to the normal weather CSV. All four are **m3 per
timestep**, not rates or depths; missing columns default to zero.

| Column | Meaning |
| --- | --- |
| `indoor_use_m3` | Delivered indoor drinking-water use |
| `garden_use_m3` | Delivered garden watering |
| `external_sewage_m3` | Outside-area wastewater entering the project sewer |
| `external_wwtp_inflow_m3` | Additional outside-area wastewater entering the WWTP directly |

Alternatively, `timeseries = "relative/path.csv"` in the table loads these columns
from a separate CSV, relative to the neighbourhood file. Its `date` labels must
be unique and exactly match every weather-row label, including initialization.
Inline columns take precedence. Nonfinite/negative values and nonzero inputs for
disabled components are rejected. As in existing runs, row zero initializes
states; its flow values are not simulated.

### Processes and parameters

- `drinking_water_loss_percent` is the percentage of network **input** lost.
	Network import = `(indoor demand + garden demand) / (1 - loss fraction)`.
	Leakage enters shallow
	groundwater directly; this assumes leakage reaches the saturated system within
	a step. There is no pressure-network or vadose pipe-leakage model.
- Garden water enters unpaved surface storage before evaporation, infiltration,
	and runoff. `garden_fraction` specifies the irrigated fraction of
	`up_no_meas_area`, excluding measure footprints. For example, `0.1` applies
	all garden water to 10% of that area. Gardens and other unpaved land have
	separate surface storage and root-zone moisture but identical soil/vegetation
	parameters. Rainfall, paved runoff, and measure-to-root-zone inflow are
	distributed uniformly in depth. Their fluxes and stores are area-weighted
	into the existing shared groundwater, open water, and measure routing.
	The default `1.0` preserves the former irrigation behaviour. Zero is allowed
	only without watering. The split operates when `drinking_water` is enabled;
	otherwise the original unpaved solver is used. Irrigation remains prescribed
	by `garden_use_m3`, with no automatic soil-moisture trigger.
- `indoor_return_fraction` enters wastewater; the remainder is an explicit
	consumptive boundary loss, not garden watering.
- `sewer_system = "separated"` requires `swds_frac = 1`: existing SWDS handles
	rain and an independent foul store handles wastewater. Pumping is limited by
	`foul_capacity_m3_day`; `foul_storage_capacity_m3` limits storage and overflow
	enters local open water. Defaults are unlimited pumping/storage and zero
	`foul_initial_storage_m3`.
- `sewer_system = "mixed"` requires `swds_frac = 0` and a positive MSS area.
	Wastewater joins existing combined runoff before pumping/overflow. Existing
	MSS storage and rainfall-derived capacities remain in force; optionally set
	`mixed_capacity_m3_day` to override the pump-to-WWTP capacity.
- `groundwater_infiltration` requires `sewer`. `sewer_depth_m` is the effective
	drainage level below the surface (m-SL); `sewer_entry_resistance_days` must be
	positive and is an effective resistance over the **groundwater compartment
	area**, not pipe-wall area. The nominal drainage rate is
	`1000 * max(sewer_depth - groundwater_depth, 0) / resistance` in mm/day.
	A storage-limited exponential step uses the previous groundwater head and
	storage coefficient, respects the groundwater bottom, and never reverses.
	Sewer surcharge feedback is deliberately not modelled. Resistance should be
	calibrated to observed infiltration; pipe geometry alone does not determine it.
- Optional `sewer_loss_percent` removes a percentage of household wastewater
	before sewer routing and adds it to groundwater. It excludes imported sewage,
	groundwater infiltration, and rain. This is prescribed exfiltration, not a
	reverse head-dependent exchange; it defaults to zero.
- `wwtp` receives local sewer pumping plus `external_wwtp_inflow_m3`.
	`wwtp_residence_days` defines a linear-reservoir delay (zero: immediate);
	`wwtp_capacity_m3_day` limits release (default unlimited). Remaining water stays
	in the plant store, initialized by `wwtp_initial_storage_m3` (default zero).
	`wwtp_local_fraction` goes to project open water; the remainder is discharged
	outside. No pollutant treatment, volumetric treatment loss, or plant bypass is
	assumed. Required receiving areas must be positive; flows are never discarded.
- `wwtp_inside_area = true` includes plant storage in the project balance and
	treats imported plant inflow and exported effluent as boundary crossings.
	With `false` (default), sewer-to-plant flow is exported and local effluent is
	imported; outside-plant storage is excluded. Without `wwtp`, sewer pumping is
	exported directly. Without `sewer`, household wastewater is exported directly.

### Results and conservation

Enabled runs add explicit volume columns, including `dw_import_m3`,
`dw_leakage_m3`, `household_wastewater_m3`, `sewer_exfiltration_m3`,
`gw_sewer_infiltration_m3`, `sewer_to_wwtp_m3`, `foul_overflow_m3`,
`wwtp_local_effluent_m3`, `wwtp_export_effluent_m3`, and infrastructure stores.
`cycle_boundary_in_m3`, `cycle_boundary_out_m3`, and `cycle_storage_m3` support
the extended project balance. Internal irrigation/leakage transfers are not
counted again as imports. Household consumptive losses appear in boundary output.
The balance report additionally exposes `urban water input` and `urban water
output`, in mm over the total project area like the existing statistics.

`sum_p_gw` includes the net pipe-related groundwater source/sink as well as the
existing percolation. `sum_r_mss` includes added wastewater in mixed mode.
Existing compartment depths remain in mm; the new `_m3` columns are volumes.

With drinking-water use enabled and a positive unpaved area, outputs also include
`garden_area_m2` and `other_unpaved_area_m2`. The prefixes `garden_` and
`other_unpaved_` identify local `init_intstor_up`, `fin_intstor_up`, `e_atm_up`,
`i_up_uz`, `r_up_meas`, `r_up_ow`, `theta_uz`, `t_atm_uz`, and `p_uz_gw`.
These depths are in mm over their own subset, not the entire unpaved area;
`theta_uz` is root-zone water storage in mm. A zero-area subset has zero outputs.
The original unprefixed columns remain area-weighted averages. For example,
`theta_uz = garden_fraction * garden_theta_uz + (1 - garden_fraction) *
other_unpaved_theta_uz`. Donor-limited capillary-rise corrections update both
the aggregate and the individual root-zone states. No new time-series columns
are needed for the garden split.
