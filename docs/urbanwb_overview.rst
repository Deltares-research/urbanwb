Urbanwb model
*************
Schematic Overview
------------------
.. _F1:
.. figure:: _build/_images/urbanwb_overview.jpg
    :width: 600px
    :height: 400px
    :scale: 100%
    :alt: alternate text
    :align: center

    Schematic overview of Urbanwb model, copied from orignal Excel-based model by Toine Vergroesen

Urbanwb model is a lumped conceptual model focusing on the water balance. Urbanwb model simulates dominant dynamic processes of an urban water system. Rainfall-runoff processes, shallow groundwater
(saturated and unsaturated zone), surface water and sewer system (combined and separate sewer system) are all incorporated
in Urbanwb. Three external water exchanges are also included with atmosphere, deep groundwater, outside water and waste water
treatment plant (WWTP). :numref:`F1` provides a schematic overview of Urbanwb model with all its fundamental elements included.
Under this conceptual framework, major dynamics in urban water system can be quickly modelled to provide users with a general
idea of how the system behaves under certain circumstances of given locations and climates.

Following is an overall introduction to the Urbanwb model. For detailed descriptions and explanations of the Urbanwb model, please
refer to "Model components" section.

In an urban area, the land use can be divided into following four types:
    * Paved area above surface level:
        + Paved roof (PR)
    * Paved area at surface level:
        + Closed paved (CP)
        + Open paved (OP)
    * Unpaved area at surface level:
        + Unpaved (UP)
    * Open (surface) water below surface level
        + Open water (OW)

Below the surface level, three components can be distinguished:
    * Unsaturated zone (UZ)
        + Since water is assumed to flow mainly vertically in the unsaturated zone, the unsaturated zone is not relevant below
          the paved roof and closed paved (PR and CP) area where the runoff flows directly to the sewer system or to the unpaved presumably
          when defined disconnected. Neither is unsaturated zone (UZ) relevant below the open paved (OP) area where the infiltration is assumed
          directly percolating into the groundwater (GW). In other words, unsaturated zone is only relevant below the unpaved (UP) area
          where the vegetation's root exists so the transpiration from the root zone must be taken into account.
    * Shallow groundwater (GW)
        + It is by default assumed no unsaturated zone is beneath the open water, thus the groundwater level is not
          relevant below open water. Though it can be defined relevant by specifying how much percentage of open water (OP) is above
          groundwater. The groundwater level below buildings can be relevant, therefore it is required to predefine the
          fraction of paved roof (PR) area that is above the groundwater level. Defining part of building (PR) and part of surface water
          (OW) that is above the groundwater level will influence the size of groundwater and thus influence calculated results since conversion
          of flux between reservoirs is dependent on area ratio of reservoirs.
    * Sewer system (SWDS and MSS):
        + Combined sewer system, i.e. mixed sewer system (MSS), collects stormwater and domestic (and industrial) wastewater
          in the same pipe system. Hence under wet weather conditions, the untreated combined sewer overflows may cause serious
          pollution to recipient water bodies (:numref:`F2`).

        .. _F2:
        .. figure:: _build/_images/mixed_sewer.jpg
            :width: 450px
            :height: 210px
            :scale: 100%
            :alt: alternate text
            :align: center

            Combined sewer system under dry, wet weather conditions, source: Wikipedia.

        + Storm water drainage system (SWDS), i.e. stormwater drainage component of the separate sewer system. Separate sewer system
          overcomes the disadvantage of combined sewer overflow pollution of combined sewer system by separately handling
          wastewater and rainwater (stormwater) in two separate systems. Only the storm water drainage part is of concern
          and incorporated in the Urbanwb.

Boundary conditions (external water exchanges) of the model:
    * Atmosphere (Atm):
        + Rainfall and potential evaporation namely Penman evaporation (i.e. potential open water evaporation) and Penman-Monteith
          evaporation (i.e. potential evapotranspiration) are the only and the most essential dynamic input (forcing) to the
          Urbanwb model. Since Urbanwb is a simplicity-based lumped conceptual model, other factors like temperature,
          relative humidity, radiation are irrelevant in the model.
    * Deep groundwater (Deep GW):
        + Seepage from shallow groundwater (GW) to the deep groundwater (deep GW) is relevant in the Urbanwb model, which can
          be specified either as a constant flux or as a dynamically-computed flux that depends on head difference and
          flow resistance.
    * Outside water and waste water treatment plant (Out and WWTP):
        + There are two outflows from model internal to this external exchange: a. Combined sewer system (MSS) is transporting
          limited water to waste water treatment plant (WWTP) located outside the study area; b. In a typical dutch polder which has
          no natural gradient for drainage, excessive water is usually pumped outside (Out) through a pumping station into a higher elevated
          network of larger primary canals (see :numref:`F3`) (and finally gets released through gravity flow during low tide or simply gets pumped into the sea).
          Both these outflows are limited by certain discharge rate. Hence, a maximum discharge capacity ("q_mss_out_cap" in model) of combined
          sewer system (MSS) to waste water treatment plant (WWTP) and a maximum discharge capacity ("pump_cap" in model) of open water (OW) to
          outside water are predefined to control the discharge from model internal to external.

        .. _F3:
        .. figure:: C:/Users/ZWX/PycharmProjects/UWM/docs/_build/_images/polder.png
            :width: 330px
            :height: 260px
            :scale: 100%
            :alt: alternate text
            :align: center

            Dutch polder system, source: Hum 300 The Arts in Society.

General assumptions of Urbanwb model:
    * Only rainfall is considered as the precipitation. It is assumed to fall instantaneously at the beginning of the current
      time step.
    * After rainfall is completed, interception evaporation during current time step starts, the rate of which is assumed
      limited by the potential open water evaporation (Penman evaporation) during that time step.
    * All the connected runoff water from paved areas will end in the sewer systems regardless of their capacities (exceedance
      of this capacity will be dealt with separately as the sewer overflow on the street). Runoff on the disconnected paved areas
      is assumed to flow to the unpaved area.
    * All relevant parameters are defined by users in accordance with local conditions of land use, soil, vegetation, surface
      water level and other related factors for their area of interest. Detailed explanations on the input is in section.
    * In terms of reservoir component B, inflow flux (in depth [mm]) from reservoir component A to reservoir component B is dependent
      on the area ratio of the two components. For instance, area of component A is :math:`5 m^2`, area of component B is
      :math:`10  m^2`, the calculated outflux from A to B in terms of A is :math:`2 mm/hr`, then the influx of B from A is :math:`2\times\frac{5}{10} = 1  mm/hr`.
      In Urbanwb, fluxes between states and state storages are computed in relation to depth ([mm]) to make sure the water quantity
      is strictly conserved not only for the individual component but also for the entire model. The parameterization of the size of components
      should be given careful concern.
    * There is no internal routing in Urbanwb model. As long as the water is added to the system, e.g. rain falls on paved
      area, during current time step it forms interception storage, and exceedance of storage capacity becomes runoff flowing
      into the sewer system. It does not takes time for water to "travel" from paved surface to the storm system.
      It would be a good analogy that a glass of water being knocked over with water spiting
      over the entire desk almost instantaneously. So the water quantity is conserved in this way, but the internal routing
      is ignored (It does not takes time for water to go from A to B).
    * Though the terminology for individual component is called paved roof and alike, it actually means area of paved roof
      (without measure) other than total paved roof area. All calculations performed on single element are related to
      area without measure. Area with measure is separately dealt with in the measure module. Please refer to the "FAQ" for
      more information.

Model components
----------------
This section explains in detail how the unit component/element of Urbanwb model is setup. The unit elements are namely
Paved roof (PR), closed paved (CP), open paved (OP), unpaved (UP), open water (OW), unsaturated zone (UZ), groundwater
(GW) and sewer system (storm water drainage system (SWDS) and combined sewer system (MSS). Their underlying principles,
simplifying assumptions, calculation orders are explained from top to bottom.

Paved roof
~~~~~~~~~~
Paved roof is mainly referred to buildings of all kinds in an urban area, which could range from low-rise buildings (e.g.
single dewlling, apartment complex) to high-rise buildings (e.g. high-rise housing, skyscraper). On a typical building roof,
a roof drainage system collects rain water in gutters and drains it to a sewer through a downspout pipe. A small amount of rainwater
ponded or intercepted on the roof surface, which is defined as interception storage in the modelling, can only be emptied through
evaporation. Excessive rainwater that exceeds the interception storage capacity limit becomes the runoff on the paved roof. Connected
runoff ends in the sewer system while disconnected runoff flows to unpaved area.

Assumptions
^^^^^^^^^^^
    * The rainwater on the paved roof is first intercepted as surface interception storage and depleted by evaporation,
      then the excessive rainwater becomes runoff. In other words, only rainfall exceeding the interception storage capacity will
      run off. Given a very large interception storage capacity, there is no runoff generated.
    * Runoff on the paved roof is redistributed to sewer system and unpaved by predefined ratios. If part of building is
      disconnected to the sewer system, for instance a small fraction of water on the roof will flow out the edge down to the
      ground, that disconnected fraction of runoff is assumed to flow to unpaved area. But the majority of runoff on the
      paved roof are connected to the sewer system, so it ends in the storm water drainage system (SWDS) and combined
      sewer system (MSS) at predefined proportions.

Calculation order
^^^^^^^^^^^^^^^^^
    * Initial interception storage at the beginning of current time step is the interception storage at the end of previous
      time step plus rainfall at current time step, and it is limited by predefined interception storage capacity on paved
      roof area.
    * (Actual) evaporation from interception on paved roof area is limited by potential open water evaporation and available initial
      interception storage during current time step. Evaporation is possible only if the interception storage contains water.
    * (Final) interception storage at the end of current time step is evaporation subtracted from initial interception storage.
    * (Total) runoff from paved roof area is rainfall minus actual evaporation minus the change in interception storage between
      current time step and previous time step. Given no measure applied or measure inflow area equals to measure
      area, there is no runoff from area of paved roof (without measure) to measure. Given measure applied, runoff on the
      differencing area between the measure inflow area and measure area will flow into the measure.
    * Subtracting runoff into the measure from the total runoff is the remaining runoff. Connected remaining runoff is
      reallocated to combined sewer system (MSS), storm water drainage system (SWDS) at predefined proportions while
      disconnected remaining runoff flows to unpavd area (UP) at predefined ratio.

Code and input parameters
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.pavedroof
    :members:
    :undoc-members: urbanwb.pavedroof.inflowfac
    :show-inheritance:

Closed paved
~~~~~~~~~~~~
Closed paved is mainly referred to impervious urban land covers, e.g. cement concrete pavement and bituminous concrete pavement.
In terms of modelling mechanisms, closed paved is quite similar to paved roof. On a typical impermeable road surface, a small amount of
rainwater is interceptied as surface ponding which can only be emptied by evaporation. Rainfall exceeding the interception storage
capacity will generate runoff, which ends in the sewer sytem through storm drians except for disconnected runoff flowing to the unpaved area by assumption.

Assumptions
^^^^^^^^^^^
    * The rainwater on the closed paved is first intercepted as surface interception storage and depleted by evaporation,
      then the excessive rainwater becomes runoff. In other words, rainfall exceeding the interception storage capacity will
      run off. Given a very large interception storage capacity on closed paved, there is no runoff generated.
    * Runoff on the paved roof is redistributed to sewer system and unpaved by predefined ratios. If part of closed paved area
      is disconnected to the sewer system, that disconnected fraction of runoff flows to unpaved area by assumption. Connected
      runoff on the closesd paved area will end in the storm water drainage system (SWDS) and combined sewer systm (MSS) at predefined
      proportions.

Calculation order
^^^^^^^^^^^^^^^^^
    * Initial interception storage at the beginning of current time step is the interception storage at the end of previous time step plus
      rainfall at current time step, and it is limited by predefined interception storage capacity on closed paved area.
    * (Actual) evaporation from interception on closed paved area is limited by the potential open water evaporation and available
      initial interception storage during current time step. Evaporation is possible only if the interception storage contains
      water.
    * (Final) interception storage at the end of current time step is evaporation subtracted from initial interception storage.
    * (Total) runoff from closed paved area is rainfall minus actual evaporation minus the change in interception storage
      between current time step and previous time step. Given no measure applied or measure inflow area equals to measure area,
      there is no runoff from area of closed paved (without measure) to measure. Given measure applied, runoff on the differencing
      area between the measure inflow area and measure area will flow into the measure.
    * Subtracting runoff into the measure from the total runoff is the remaining runoff. Connected remaining runoff is reallocated
      to combined sewer system (MSS) and storm water drainage system (SWDS) at predefined proportions while disconnected runoff
      flows to unpaved area (UP) at predefined ratios.

Code and input parameters
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.closedpaved
    :members:
    :undoc-members:
    :show-inheritance:

Open paved
~~~~~~~~~~
Open paved are paths, sidewalks, parking area and other less impervious city-fabric type that has limited infiltration capacity.
These permeable pavements may use porous material that allows water flowing through it (e.g. pervious concrete, porous asphalt)
or nonporous material that are spaced (e.g. paving stones, permeable interlocking concrete pavement) so the water may infiltrate
between the cracks. Consequently, compared to paved roof and closed paved component, open paved component has one extra
infiltration flux from open paved surface to groundwater, which is limited by the infiltration capacity as well as available
surface interception storage.

        .. figure:: _build/_images/permeable_pavement.jpg
            :scale: 85%
            :alt: alternate text
            :align: center

            Fig: 2.1: Permeable pavement --- porous asphalt and interlocking pavement, source: google images.

Assumptions
^^^^^^^^^^^
    * Cracks on the pavement and pores in the material that allow infiltration only occupy a very minor fraction of the
      open paved surface area, hence it does not affect the interception storage on the open paved surface.
    * Infiltration starts after interception storage is filled. Interception storage can only be emptied by evaporation.
    * There is hardly any plant under the open paved area, thus no transpiration from the root zone is relevant. Hence,
      for simplicity, the infiltration from open paved surface is assumed directly percolating into the groundwater without going
      through the unsaturated zone.

Calculation order
^^^^^^^^^^^^^^^^^
    * Initial interception storage at the beginning of current time step is the interception storage at the end of previous
      time step plus rainfall at current time step, and it is limited by predefined interception storage capacity on open paved area.
    * (Actual) evaporation from interception on open paved area is limited by potential open water evaporation and available
      initial interception storage during current time step. Evaporation is possible only if the interception storage contains water.
    * (Final) interception storage at the end of current time step is evaporation subtracted from initial interception storage.
    * The infiltration occurs if interception storage gets fully filled. Infiltration is limited by predefined infiltration
      capacity on open paved. Infiltration directly flows to groundwater, i.e. percolation (skipping unsaturated zone).
    * Runoff from open paved area is rainfall minus actual evaporation minus change in interception storage between current time
      step and previous time step minus percolation to groundwater. Runoff is allocated to combined sewer system, storm water drainage
      system and unpaved area based on input parameters of predefined ratios.

Code and input parameter
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.openpaved
    :members:
    :undoc-members:
    :show-inheritance:

Unpaved
~~~~~~~
Unpaved area is land use that has no hard impervious surface cover, e.g. gardens and grassland, on which the water can much
more easily infiltrate than on paved area. Vegetation/crop type on the unpaved needs to be predefined. The model assumes
notable distinction between paved area (PR, CP, OP) and unpaved area (UP). On paved area, the runoff is mainly drained through
the sewer system except for disconnected runoff which is assumed to unpaved area. In contrast, on unpaved area, the water contained
in the interception storage simultaneously evaporates to atmosphere and infiltrates to unsaturated zone, futher percolates to
groundwater and then gets drained to deep groundwater reservoir and open water, while the water exceeding the interception storage
capacity becomes runoff which is assumed to flow to open water.

Assumptions
^^^^^^^^^^^
    * The runoff water from disconnected paved area is equally spread over the unpaved area. This runoff water is added to
      the water available for infiltration instead of the interception.
    * The interception capacity for unpaved area is defined as the water depth above which surface runoff starts. Interception
      capacity of vegetation is not separately defined. Evaporation from vegetation is taken up in the transpiration from the unsaturated
      zone. Evaporation and infiltration from the unpaved surface  will occur as long as water remains on surface level.
    * Infiltration starts after interception storage is filled (i.e. storage contains water). Interception storage
      is proportionally emptied by infiltration and evaporation. Infiltration is limited by the actual infiltrate capacity
      or the available soil moisture storage. Evaporation is limited by the potential open evaporation of that time step.
    * Actual infiltration capacity is limited by the actual storage capacity in the root zone, i.e. the maximum moisture content minus
      the actual moisture content. However the anticipated percolation from rootzone to groundwter during the current time step allows more infiltration.
      The anticipated percolation is limited by the saturated conductivity of the soil and the maximum moisture content minus
      the actual moisture content of that time step.
    * Time factor is the part of the time step that water is remaining on surface level. Potential open water evaporation is multiplied
      with the time factor to get the actual evaporation of that time step. The actual infiltration capacity is multiplied with
      the time factor to get the actual infiltration of that time step.
    * All runoff water will flow to the open water area. For now, runoff from unpaved is assumed to flow to the open water area.
      If no open water area is present the water cannot runoff and will be stored on the surface of the unpaved. In that case the
      water can only evaporate or infiltrate.

Calculation orders:
^^^^^^^^^^^^^^^^^^^
    * Total runoff from disconnected paved area is the sum of runoff from disconnected paved area (PR, CP, OP) to unpaved area (UP).
      The conversion is dependent on the area ratio.
    * Initial interception storage on land is the final storage at the end of previous time step plus precipitation at
      current time step plus total runoff from disconnected paved area. It is not limited by interception storage capacity.
      Hence, initial interception storage is a transition variable (temporary variable) which is only relevant in calculation processes.
    * (Actual) infiltration capacity is limited by the infiltration capacity of the soil and the available free space in
      rootzone for infiltration. Available free space for infiltration is limited by maximum moisture content of the
      rootzone minus moisture content of previous time step plus anticipated percolation. Anticipated percolation is
      limited by saturated conductivity of the soil and maximum moisture content of the rootzone minus moisture content
      of previous time step.
    * As stated before, time factor is part of time step that water is remaining on the surface level and the water in
      the interception storage is emptied by evaporation and infiltration only. Hence the time factor at current time
      step is limited by 1 and the ratio of initial interception storage calculated above over the sum of potential evaporation and actual
      infiltration capacity during current time step.
    * (Actual) evaporation is potential evaporation multiplied by time factor.
    * (Actual) infiltration is actual infiltration capacity multiplied by time factor.
    * (Final) interception storage on land is limited by predefined interception storage capacity on land and initial storage
      on land minus evaporation and infiltration. For now, runoff from unpaved area is assumed to flow to the open water.
      If no open water area is present the water cannot runoff and will be stored on unpaved land surface in which case water can only
      evaporate or infiltrate. In fact if that case, a larger predefined value of storage capacity on unpaved should be applied.
      Therefore, it is highly recommended for now to apply a tiny fraction of open water even if there is no open water in area of interest.
    * Runoff on the unpaved is the interception storage after evaporation and infiltration that still exceeds the interception storage
      capacity. If there is no open water defined, the water will not run oof and only be stored on land surface being emptied
      by evaporation and infiltration only.

Code and input paraemeter
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.unpaved
    :members:
    :undoc-members:
    :show-inheritance:

Unsaturated zone
~~~~~~~~~~~~~~~~
Unsaturated zone is underneath unpaved area. Rootzone below paved area is irrelevant thus unsaturated is assumed to has
the same area as unpaved area. Unsaturated zone receives infiltration flux from unpaved area as inflow and takes percolation
from unsaturated zone to groundwater as outflow. Percolation flux is limited by the saturated permeability of the soil.
Transpiration of plants (root zone water uptake) is modelled as the product of potential evapotranspiration for reference crop
and transpiration reduction coefficient. Transpiration reduction coefficient is a concept from the literature [Feddes]_.
Figure below shows how the transpiration reduction factor (i.e. so called water stress
coefficient in [Dejongvanlier]_, figure also copied from this reference) is related to soil water pressure head.
h = relative root zone storage = moisture content / moisture content at equilibrium.
In the range between :math:`h_3` (reduction point)
and :math:`h_2` (field capacity), root water uptake is optimal, so :math:`\alpha_{rw}=1`. When :math:`h < h_3`, :math:`\alpha_{rw}` linearly
reduces to zero at :math:`h_4` (fully saturated). The threshold pressure :math:`h_3` increases with potential transpiration
rates, i.e. daily crop-evaporation. For low potential transpiration rate, the threshold pressure :math:`h_{3l}` is lower
than the threshold pressure :math:`h_3h` at high potential transpiration rate. Simplifications are made here to calculate
daily crop-evaporation values. For hourly case, instead of using sum of 24 hour evaporation on specified day (daily value),
we use hourly evaporation divided by :math:`2\Delta t (i.e. 2\times\frac{1}{24})` since it is assumed crop-evaporation occur only during daytime.

.. figure:: _build/_images/transpiration.jpg
    :width: 600px
    :height: 300px
    :scale: 100%
    :alt: alternate text
    :align: center

    Fig: 2: Transpiration reduction coefficient, copied from the literature [Dejongvanlier]_

Assumptions
^^^^^^^^^^^
    * The infiltration water from the open paved area flows directly to groundwater (percolation) without passing unsaturated zone.
    * The area of unsaturated zone is equal to area of the unpaved.
    * For timestep length :math:`\Delta t` smaller than 1 day, daily crop-evaporation to determine moisture content at reduction point h3 is
      by simplification the potential evapotranspiration rate divided by 2t because it is assumed that (crop-) evaporation occurs during half
      a day (only during daytime). Actually it would be better to apply daily reference crop evaporation instead of reference crop
      evaporation at current time step divide :math:`2\Delta t`.
    * (Actual) transpiration is determined by transpiration reduction factor and potential reference crop evaporation during current time step.
    * Percolation to groundwater is limited by the saturated conductivity of the soil.

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Total infiltration from unpaved area is taken as the influx. For that sizes of different runoff areas are multiplied with
      different runoff depths of these areas. The sum is divided by the size of the unpaved(unsaturated zone) area.
    * Calculate drought evaporation reduction moisture content :math:`\theta_{h3}`. When daily potential evaporation is less than 1 mm/d
      :math:`\theta_{h3} = \theta_{h3l}`, and if daily potential evaporation is more than 5 mm/d, :math:`\theta_{h3} = \theta_{h3h}`.
      If daily potential evaporation is between 1mm/d and 5 mm/d, :math:`\theta_{h3}` is interpolated between :math:`\theta_{h3l}`
      and :math:`\theta_{h3h}`.
    * Determine transpiration reduction factor by linear interpolation between :math:`\theta_{h1}` (completely saturated moisture content),
      :math:`\theta_{h2}` (field capacity moisture content), :math:`\theta_{h3}` (drought evaporation reduction moisture
      content), :math:`\theta_{h4}` (permanent wilting point moisture content), based on actual root zone moisture content
      of the previous time step and the infiltration from the unpaved area.
    * Evapotranspiration from unsaturated zone at current time step is the product of transpiration reduction factor and
      reference crop evaporation.
    * Determine equilibrium root zone moisture content :math:`\theta_{eq}` by interpolation, based on the groundwater level
      at previous time step. During the current time step, the equilibrium root zone moisture content :math:`\theta_{eq}` is
      interpolated from the equilibrium moisture content  values in the root zone at two groundwater level in the database table which are
      respectively below and above groundwater level at previous time step.
    * Determine the maximum capillary rise by interpolation, based on groundwater level at the previous time step.
      The maximum capillary rise is related to the groundwater level and the soil type. For a number of predefined soil types
      a basic table is available in database. Similarly to the equilibrium moisture content in the root zone the maximum
      capillary rise is interpolated from the two groundwater levels.
    * Percolation from unsaturated zone to groundwater can be positive (downward) and negative (upward, i.e. capillary rise).
      Hence percolation are determined for two situations: If rootzone moisture content at the end of previous time step plus
      infiltration minus evapotranspiration is greater than equilibrium root zone moisture content, then it is downward percolation,
      otherwise it is upward capillary rise. For downward percolation, it is limited by saturated conductivity
      of the soil and difference towards equilibrium root zone moisture content; For upward capillary rise, it is limited by
      maximum capillary rise and different towards equilibrium root zone moisture content.
    * The root zone moisture content at the end of current time step is then the root zone moisture content at the end
      of the previous time step plus infiltration minus evapotranspiration minus percolation which are all calculated above.

Code and input parameter
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.unsaturatedzone
    :members:
    :undoc-members:
    :show-inheritance:

Groundwater
~~~~~~~~~~~
Groundwater component takes percolation flux from unsaturated zone and infiltration flux from open paved
as inflows. The outflows are downward seepage drainage flux to deep groundwater and seepage drainage flux to open
water. Outflow’s direction is driven by head difference, thus it can be positive or negative, it is like a two-way street.
The groundwater area is equal to the total area minus the open water area that is not above the groundwater and part of
the paved roof area (buildings) of which the basement is below groundwater. Maximum capillary rise and storage coefficient
for limiting percolation and calculating root zone moisture content are determined by interpolation based
on groundwater level at previous time step. Groundwater level is calculated as below, in which P is percolation,
:math:`q_s=\frac{H-h}{c}` is seepage, :math:`q_{d}=\frac{pp-h}{w}` is drainage (inflow) and all levels are related to ground level:

.. figure:: C:/Users/ZWX/PycharmProjects/UWM/docs/_build/_images/groundwater.jpg
    :width: 600px
    :height: 300px
    :scale: 100%
    :alt: alternate text
    :align: center

    Figure 3: Groundwater component fluxes calculation

.. math::

    \because \frac{dh(t)}{dt} = \frac{q_{in}}{\mu}=\frac{q_s(t)+q_d(t)+P}{\mu} = \frac{\frac{H-h(t)}{c}+\frac{pp-h(t)}{w}+P}{\mu} \\
     = \frac{H\cdot w+pp\cdot c+P\cdot c\cdot w}{\mu c w} - \frac{w+c}{\mu\cdot c\cdot w}h(t)

    \therefore \frac{\mu\cdot c\cdot w}{w+c}\cdot \frac{dh(t)}{dt}=\frac{H\cdot w+pp\cdot c+P\cdot c\cdot w}{w+c} - h(t)

    \because A\cdot \frac{dx}{dt} = B - x \Rightarrow x=K_1 e^{-\frac{t}{A}}+B

    t = 0 \Rightarrow h(t) = h_0 = K_1 + B

    \because A = \frac{\mu\cdot c\cdot w}{w+c}, B = \frac{H\cdot w+pp\cdot c+P\cdot c\cdot w}{w+c}

    \therefore h(t) = B + (h_0 - B)\cdot e^{-\frac{t}{A}}

    \therefore h(t) = \frac{H\cdot w+pp\cdot c + P\cdot c\cdot w}{w+c}+(h_0 - \frac{H\cdot w+pp\cdot c+P\cdot c\cdot w}{w+c})\cdot e^{-t\cdot \frac{w+c}{\mu\cdot w\cdot c}}

Assumptions
^^^^^^^^^^^
    * The infiltration water from the open paved area flows directly to groundwater (percolation) skipping unsaturated zone.
    * The groundwater area is equal to the total area minus part of the surface open water area below phreatic table and
      part of the paved roof area of which the basement is below groundwater.
    * Drainage and seepage are based on the groundwater level at the end of previous time step. Drainage and seepage
      are somewhat reduced due to the changing groundwater level caused by the fluxes. It means higher the head difference
      between shallow groundwater and deep groundwater (or open water), higher the driving force, greater the drainage flux.
      With fluxes exchanging, head difference gets smaller, so the flux gets smaller.

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Percolation is the total sum of percolation from open paved and percolation from unsaturated zone which is related to the
      area conversion ratio between different components. The sizes of the different percolation areas are multiplied with
      different percolation depths of these areas. The sum is divided by the size of the groundwater area.
    * Determine storage coefficient :math:`\mu` by linear interpolation, based on the storage coefficients of the two groundwater
      levels above and below the actual groundwater level at the previous time step in the database table.
    * Determine new groundwater level based on seepage, drainage and percolation flux. See the illustration plot and calculation formulas above.
      In my opinion, it means based on a. how seepage to deep GW is defined? As a constant flux or as a
      dynamic flux and b. the head difference (driving force) between the groundwater level and open water level.
    * Determine downward seepage flux to deep groundwater (can also be upward negative) during current time step
      according to predefinition. You can either define a constant flux (0=flux) or a fixed deep groundwater hydraulic
      head plus a vertical drainage resistance vc (1=level).
    * Determine drainage to open water during current time step based on the mass balance: drainage water = inflowing
      water - outflowing water - stored groundwater. Note here the drainage flux is not related to drainage resistance w
      which is related in groundwater level calculation. It is only dependent on the water balance.
    * Determine (final) groundwater level below surface level and above surface level at the end of the current time step,
      dependent on groundwater level at the end of previous time step, percolation, seepage, drainage flux and storage coefficient :math:`\mu`.


Code and input parameter
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.groundwater
    :members:
    :undoc-members:
    :show-inheritance:

Sewer system
~~~~~~~~~~~~
Sewer system is combined of storm water drainage system (SWDS) and combined sewer system (MSS) of
which the sewer system capacity should be accordingly predefined in regard to local context. Sewer system consists of
mixed sewer system (MSS) (i.e. combined sewer system) and storm water drainage system (SWDS) (i.e. storm drain part of
separate sewer system). As we know, there are two phases for combined sewer system. During dry flow condition, all runoff
is tranported to the waste water treatment plant (WWTP) for futher treatment, while during wet flow conidtion (large storms),
the relief structure (CSO weir) allows major part of the combined stormwater and sewage to be discharged untreatedly to
an adjacent water body. So in phase one, combined sewer system collects runoff from paved areas and discharges it to
waste water treatment plant (WWTP) which is limited by a predefined discharge capacity above which the sewer overflow
through CSO weir to open water will occur. Given a heavier rainfall event, we enter phase two --- combine sewer overflow
occurs, however if the discharge capacity from Combined sewer system to open water is still exceeded because of e.g. quite heavy
rainfall, then sewer overflow onto the street will occur. Different from combined sewer system (MSS), Storm water drainage
system (SWDS) drains strom water directly to the open water and the discharge is limited by predefined discharge capacity
above which the sewer overflow on the street will occur.

Assumptions:
^^^^^^^^^^^^
    * Sewer system component is a bit confusing, especially the discharge capacity part. It is developed based on NL case,
      hence user must understand it and tailor the input for more realistic modelling.
    * Runoff from paved areas to sewer system is partitioned to combined sewer system and storm water drainage system at predefined
      proportions.
    * Area of sewer system is equal to the total area of all connected paved areas (PR, CP, OP).

Calculation orders:
^^^^^^^^^^^^^^^^^^^
    * Determine total runoff from paved areas (PR, CP, OP) to storm water drainage system (SWDS) during the current time step.
      The depth is related to the area ratio.
    * Determine total runoff from paved areas (PR, CP, OP) to combined sewer system (MSS) during the current time step.
      The depth is related to the area ratio.
    * Determine outflow from storm water drainage system to open water during current time step based on storage in SWDS
      at previous time step, runoff from paved areas and it is limited by the predefined discharge capacity of the storm
      water drainage system which is in fact the storm water drainage capacity to open water above which water will overflow
      onto the street. In the Netherlands this is designed to occur once every two year.
    * Determine outflow from combined sewer system to waste water treatment plant during current time step which is limited by
      predefined discharge capacity of the combined sewer system to WWTP which is in fact the sewer discharge capacity above
      which the combined sewer overflow to open water will occur. In the Netherlands this is designed to occur six to seven times a year.
    * Determine outflow from combined sewer system to open water during current time step which is limited by the predefined
      discharge capacity of the combined sewer system to open water which is in fact the combined sewer discharge capacity to
      open water above which water will overflow onto the street. In the Netherlands this is designed to occur once every two year.
    * Determine sewer overflow on the street of storm water drainage system during current time step. It is assumed overflow water is
      drained the same time step to open water.
    * Determine sewer overflow on the street of combined sewer system during current time step. It is assumed overflow water is drained
      the same time step to open water.
    * Determine storage in the storm water drainage system at the end of current time step. Storage is only used when
      the discharge capacity is exceeded by the inflow volume. Storage is limited by the storage capacity.
      All other excess water will result in overflow.
    * Determine storage in the combined sewer system at the end of current time step. Storage is only used when the
      discharge capacity is exceeded by the inflow volume. Storage is limited to the storage capacity. All other excess
      water will result in overflow.

Code and input parameter
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.sewersystem
    :members:
    :undoc-members:
    :show-inheritance:

Open water
~~~~~~~~~~
Open water is the summation of all the control open water bodies, e.g. ditches, canals and
ponds in a polder. It receives runoff from unpaved, sewer system, groundwater. It is more like an abstract component that reflects
the system storage situation. Target open water level is set as reference open water level (down limit). Under heavy rain events,
open water level may exceed the target level, indicating there will be overflow runoff (excessive water needs to be stored)
in the the model internal, which reflected in reality are all kinds of urban flood/inundation phenomenons. We calculate
the maximum storage height above the target open water level with the model. That maximum storage height averaged over
the entire study domain is reflecting the required storage capacity in depth for the study domain. (Sewer system and Open
water needs more explanations.)

Assumptions
^^^^^^^^^^^

Calculation orders
^^^^^^^^^^^^^^^^^^

    * Determine direct rainfall and evaporation during current time step.
    * Determine total runoff (from unpaved area) to open water during current time step.
    * Determine drainage from groundwater to open water during current time step.
    * Determine total outflow from sewer systems to open water during current time step.
    * Determine total sewer overflow on the street from sewer systems (to open water) during current time step.
    * Determine inflow from measure area (if applicable) during current time step.
    * Determine discharge from open water to outside water during current time step.
      When open water level is above this predefined target open water level,
      discharge to outside water (model external) starts, and the discharge is limited by the predefined pump capacity.
      Note that the outside water is not part of the model, and the pump capacity here is Q in the storage-discharge-frequency
      curve.
    * Determine open water level at the end of the current time step.


Code and input parameters
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: urbanwb.openwater
    :members:
    :undoc-members:
    :show-inheritance:

FAQ
---
1. What is measure inflow area ( ,area with measure and area without measure)?

    .. figure:: _build/_images/measure_inflow.png
        :width: 350px
        :height: 220px
        :scale: 100%
        :alt: alternate text
        :align: center

        Fig: 3.1: Illustration of measure inflow area

As can be seen from the figure 3.1 above, we take paved roof component as an example to explain several concepts users may
find confusing. Total_pr_area means the entire paved roof area, so the big rectangle in the figure, the area of which is
say 20 m2. In this paved roof area, if a 3 m2 green roof measure (small green rectangle) is implemented on the paved roof,
we call this green rectangle "paved roof with measure" (pr_meas_area). So subtracting this area from the entire area,
we have "paved roof without measure" (pr_no_meas_area), the area of which should be 20 - 3 = 17 m2. Besides these easy-to-understand
concept, there is a concept called measure inflow area, that means the runoff inflow area to measure on the paved roof, which
in the figure is the dashed-line blue rectangle. The measure inflow area should contain the measure area --- measure inflow area >=
pr_meas_area, in the figure say it is 8 m2. The difference between the measure inflow area and pr_meas_area is 8-3=5m2. So runoff on this 5m2
out of the pr_no_meas_area (17 m2) will inflow into the measure.


Parameter estimation
--------------------

References
----------
.. [Feddes] FEDDES, Reinder Auke. Crop factors in relation to Makkink reference-crop evapotranspiration. 1987.
.. [Dejongvanlier] DE JONG VAN LIER, Q., et al. Macroscopic root water uptake distribution using a matric flux potential approach. Vadose Zone Journal, 2008, 7.3: 1065-1078.
