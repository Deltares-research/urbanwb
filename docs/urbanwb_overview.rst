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

Urbanwb model is a lumped conceptual model for urban water balance modelling. Urbanwb model simulates dominant dynamic hydrological
processes of an urban water system. Rainfall-runoff processes, shallow groundwater (saturated and unsaturated zone), surface
water and sewer system (combined and separate sewer system) are all incorporated in Urbanwb model. Three external water
exchanges are included with atmosphere, deep groundwater, outside water and waste water treatment plant (WWTP). :numref:`F1`
provides a schematic overview of Urbanwb model with its fundamental elements included. Under this conceptual framework,
major hydrological dynamics in an urban water system can be quickly and indicatively modelled to provide users with a general
idea of the water quantity distribution amd how the water system behaves under certain circumstances.

Following provides an overall introduction to the Urbanwb model. For detailed descriptions and explanations of the Urbanwb model, please
refer to "Model components" section.

In an urban area, the land use is divided into four types:
    * Paved area above surface level:
        + Paved roof (PR)
    * Paved area at surface level:
        + Closed paved (CP)
        + Open paved (OP)
    * Unpaved area at surface level:
        + Unpaved (UP)
    * Surface water below surface level
        + Open water (OW)

Below the surface level, three components are distinguished:
    * Unsaturated zone (UZ)
        + Since water is assumed to flow mainly vertically in the unsaturated zone, unsaturated zone is irrelevant below
          paved roof (PR) and closed paved (CP) where runoff flows directly into sewer system (SWDS, MSS) or to unpaved
          (UP) when defined disconnected. Unsaturated zone (UZ) is neither relevant below open paved (OP) where the limited
          infiltration is assumed percolating directly into groundwater (GW). In other words, unsaturated zone (UZ) is only
          relevant below unpaved (UP) area since transpiration from the root zone has to be taken into account.
    * Shallow groundwater (GW)
        + By default it is assumed no unsaturated zone (UZ) is beneath open water (OW), thus the groundwater level is irrelevant
          below open water, though it can be defined relevant by specifying the percentage of open water (OW) that is above
          phreatic table. The groundwater below buildings is relevant and it is required to predefine the percentage of
          paved roof (PR) that is above the groundwater level. Flux conversion between reservoirs depends on the area ratio
          of reservoirs.
    * Sewer system (SWDS and MSS):
        + Combined sewer system, i.e. mixed sewer system (MSS), collects stormwater and domestic (and industrial) wastewater
          in the same pipe system. Under wet weather conditions, untreated combined sewer overflows may cause serious
          pollution to recipient water bodies (:numref:`F2`).

        .. _F2:
        .. figure:: _build/_images/mixed_sewer.jpg
            :width: 450px
            :height: 210px
            :scale: 100%
            :alt: alternate text
            :align: center

            Combined sewer system under dry, wet weather conditions, source: Wikipedia.

        + Storm water drainage system (SWDS), i.e. stormwater drainage component of the separate sewer system. Separate
          sewer system overcomes the drawback of sewer overflow pollution of combined sewer system through disposing wastewater
          and stormwater in two separate systems. The storm water drainage system module is incorporated in the Urbanwb
          model.

Boundary conditions (external water exchanges) of the model:
    * Atmosphere (Atm):
        + Rainfall and potential evaporation namely Penman evaporation [Penman]_ (i.e. potential open water evaporation)
          and Penman-Monteith evaporation [Monteith]_ (i.e. potential evapotranspiration) are the only forcing to Urbanwb
          model. Since Urbanwb is a simple lumped conceptual model, other factors like temperature, relative humidity,
          radiation and etc are irrelevant.
    * Deep groundwater (Deep GW):
        + Seepage from shallow groundwater (GW) to deep groundwater (deep GW) can be defined relevant in Urbanwb model,
          either as a constant flux or a dynamically-computed flux dependent on head difference and flow resistance.
    * Outside water and waste water treatment plant (Out and WWTP):
        + There are two outflows from model internal to this external exchange: a. Combined sewer system (MSS) discharges
          water at certain rate to waste water treatment plant (WWTP) which is located outside the study area; b. excess
          of water on the surface water is pumped outside. These outflows are limited by predefined discharge rate --- the
          maximum discharge capacity of combined sewer system (MSS) to waste water treatment plant (WWTP)
          and the maximum discharge capacity of open water (OW) to outside water.

    .. note::
          A typical dutch polder has no natural gradient for drainage, thus excessive water is normally pumped through a
          pumping station into a higher elevated network of larger primary canals (:numref:`F3`) from where the water
          is released into sea at low tide.

        .. _F3:
        .. figure:: _build/_images/polder.png
            :width: 330px
            :height: 260px
            :scale: 100%
            :alt: alternate text
            :align: center

            Dutch polder system, source: Hum 300 The Arts in Society.

General assumptions of Urbanwb model:
    * Only rainfall is considered as the precipitation. Rainfall falls instantaneously at the beginning of
      current time step.
    * After rainfall is completed, interception evaporation during current time step starts, the rate of which is limited
      by the potential open water evaporation at the same time step.
    * Connected runoff from paved areas ends in the sewer systems regardless of their capacities (exceedance
      of this capacity is dealt with separately as sewer overflow on the street). Runoff from disconnected paved area
      flows to unpaved area.
    * All relevant parameters are defined by users in accordance with local conditions of area of interest, like land use,
      soil, vegetation, surface water level and etc. Detailed explanations on parameter input is in section ???.
    * Calculated fluxes and states are expressed in depth (mm) per area of that component. For reservoir B, inflow flux
      from reservoir A to B is converted from outflow flux from A by considering the area ratio of reservoir A over B.
      For example, area of A is :math:`5 m^2`, area of B is :math:`10  m^2`, calculated outflux from A to B in terms of
      A is :math:`2 mm/hr`, then the influx of B from A  in terms of B is :math:`2\times\frac{5}{10} = 1  mm/hr`.
      In Urbanwb model, the water quantity is strictly conserved not only for the individual reservoir but also for the
      entire model.
    * Internal routing is irrelevant in Urbanwb model. It takes no time for water to "travel" between reservoirs.
      Consequently, the model is applicable at neighbourhood scale and use at large spatial scale may be questionable. A
      best analogy would be a glass of water being knocked over with water spilling all over the table instantly --- mass
      balance is conserved but routing is ignored.
    * Urban adaptation measures can be implemented with Urbanwb model through incorporating Adaptive Measure module. Measure
      module is an individual component that interacts with basic reservoirs of Urbanwb model. Detailed explanations on
      adaptive measure structure is in Section ???.
    * Parameters to initialize the model are allocated into two parts and saved in separate configuration files. In neighbourhood
      configuration file, parameters of local urban environment like land use fractions, soil type, target water level
      and etc are stored. In measure configuration file, parameters to setup the measure are stored. Parameters should be
      defined by user from scientific literature and empirical evidence with his or her logistic thinking and expert judgement
      in order to avoid "Garbage in, garbage out".
    * The flux from A to  B (e.g. infiltration) is limited from three aspects: a. how much water (storage) is available for
      transferring b. how much space is left in recipient B to accommodate the water c. What is the transport capacity between
      A and B.

Model components
----------------
This section explains in detail how each of the unit components of Urbanwb model is architected. Unit elements involved are namely
paved roof (PR), closed paved (CP), open paved (OP), unpaved (UP), open water (OW), unsaturated zone (UZ), groundwater
(GW) and sewer system (SWDS and MSS). Their underlying principles, simplifying assumptions, and calculation orders are explained
in depth from top to bottom in this section. Note that the mentioned area of these individual units eg. Paved roof in the modelling
is the area of PR (without measure) instead of total area of PR, the differentiations between these area-related terms are talked about
in FAQ section.

Paved roof
~~~~~~~~~~
Paved roof (PR) refers to all kinds of buildings in an urban area ranging from low-rise buildings (e.g. single dwelling,
apartment complex) to high-rise buildings (e.g. high-rise housing, skyscraper). On rooftop, a roof drainage system collects
rainwater in gutters and drains it into a sewer through a downspout pipe. A small amount of rainwater ponded or intercepted
on the roof surface is defined as interception storage. It can be emptied only through evaporation. Water exceeding the
interception storage capacity becomes runoff on the paved roof. Connected runoff (runoff on the roof that is connected to
sewer system) ends in the sewer system while disconnected runoff flows to unpaved area by assumption. Below is the schematic
overview of paved roof (see :numref:`F4`).

        .. _F4:
        .. figure:: _build/_images/Pavedroof.jpg
            :width: 600px
            :height: 450px
            :scale: 100%
            :alt: alternate text
            :align: center

            Schematic overview of Paved Roof (PR)

Assumptions
^^^^^^^^^^^
    * Rainwater falling on the building roof is first retained as interception storage and depleted by evaporation,
      and then excess water becomes runoff. In other words, only rainfall exceeding interception storage capacity runs
      off. Provided that a considerably large interception storage capacity on paved roof is predefined, there is no runoff generated.
    * (Connected) runoff on paved roof is redistributed to sewer systems (SWDS and MSS) and unpaved (UP) by predefined ratios.
      If part of roof is disconnected to sewer system, for instance a minor fraction of water flows out from the roof edge down
      to the ground directly, that disconnected fraction of runoff is assumed to flow to unpaved area. However, given a normally functioning
      roof drainage system, the majority of the runoff from paved roof contributes to the storm water drainage system (SWDS) or (and) combined
      sewer system (MSS) at predefined proportions.

Calculation order
^^^^^^^^^^^^^^^^^
    * Initial interception storage on paved roof at the beginning of current time step is the remaining interception storage on paved roof
      at the end of previous time step plus rainfall at current time step, and it is limited by predefined interception storage
      capacity on paved roof.
    * (Actual) evaporation from interception on paved roof during current time step is limited by potential open water evaporation
      and available initial interception storage on paved roof during the same time step. Evaporation is possible only if the interception
      storage contains water.
    * (Final) interception storage on paved roof at the end of current time step is evaporation subtracted from initial interception storage.
    * (Total) runoff from paved roof during current time step is rainfall subtracting actual evaporation and the change in interception
      storage between the same time step and previous time step. Total runoff from paved roof are redistributed to the measure (Meas),
      sewer system (SWDS and MSS) and unpaved (UP) at predefined ratios.
    * Subtracting the runoff to the measure from total runoff is the remaining runoff. Connected remaining runoff is
      reallocated to storm water drainage system (SWDS) and combined sewer system (MSS) at predefined proportions while
      disconnected remaining runoff flows to unpaved area (UP) at predefined ratio.

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.pavedroof
    :members:
    :undoc-members:
    :show-inheritance:

Closed paved
~~~~~~~~~~~~
Closed paved is mainly referred to impervious urban land covers, e.g. roads, parking lots, paved driveways, asphalt street and etc.
that are made of impermeable material like cement concrete pavement and bituminous concrete pavement. In terms of conceptual modelling
mechanisms, closed paved is quite similar to paved roof. On the surface of a typical impermeable road, a small amount of rainwater is
intercepted as surface ponding which can only be emptied through evaporation. Rainfall exceeding the interception storage capacity will
generate runoff, which flows to the sewer sytem (SWDS and MSS) through storm drains except for the disconnected fraction of runoff flows
to the unpaved area (UP) by assumption. Below is the schematic overview of closed paved (see :numref:`F5`).

        .. _F5:
        .. figure:: _build/_images/Closedpaved.jpg
            :width: 600px
            :height: 450px
            :scale: 100%
            :alt: alternate text
            :align: center

            Schematic overview of Closed paved (CP)

Assumptions
^^^^^^^^^^^
    * Rainwater falling on the closed paved is first ponded as surface interception storage and depleted by evaporation,
      then the excessive rainwater becomes runoff. In other words, only rainfall exceeding the interception storage capacity
      runs off. Provided that a very large interception storage capacity on closed paved is predefined, there is no runoff
      generated.
    * Runoff on the closed paved is redistributed to sewer system (SWDS and MSS) and unpaved (UP) by predefined ratios. If part
      of closed paved area is disconnected to the sewer system, that disconnected fraction of runoff flows to unpaved area by
      assumption. Connected runoff on closed paved flows to the storm water drainage system (SWDS) or (and) combined sewer
      system (MSS) at predefined proportions.

Calculation order
^^^^^^^^^^^^^^^^^
    * Initial interception storage on closed paved at the beginning of current time step is the remaining interception storage on
      closed paved at the end of previous time step plus rainfall at current time step, and it is limited by predefined interception
      storage capacity on closed paved.
    * (Actual) evaporation from interception on closed paved during current time step is limited by potential open water
      evaporation and available initial interception storage on closed paved during the same time step. Evaporation is possible only if the
      interception storage contains water.
    * (Final) interception storage on closed paved at the end of current time step is evaporation subtracted from initial interception storage.
    * (Total) runoff from closed paved during current time step is rainfall subtracting actual evaporation and the change in interception storage
      between the same time step and previous time step. Total runoff from closed paved is redistributed to the measure (Meas),
      sewer system (SWDS and MSS) and unpaved (UP) at predefined ratios.
    * Subtracting the runoff to the measure from the total runoff is the remaining runoff. Connected remaining runoff is reallocated
      to storm water drainage system (SWDS) and combined sewer system (MSS) at predefined proportions while disconnected remaining runoff
      flows to unpaved area (UP) at predefined ratios.

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.closedpaved
    :members:
    :undoc-members:
    :show-inheritance:

Open paved
~~~~~~~~~~
Open paved are paths, sidewalks, parking area and other less impervious urban land cover that has relatively limited infiltration capacity.
These permeable pavements use porous material that allows water flowing through it (e.g. pervious concrete, porous asphalt)
or spaced nonporous material (e.g. paving stones, permeable interlocking concrete pavement) that allows water infiltrate between the
cracks (see :numref:`F6`). Consequently, compared to paved roof (PR) and closed paved (CP) component, open paved (OP) component has one extra
infiltration flux from open paved surface to groundwater, which is limited by the infiltration capacity as well as available interception
storage on open paved. :numref:`F7` shows the schematic overview of open paved.

        .. _F6:
        .. figure:: _build/_images/permeable_pavement.jpg
            :scale: 85%
            :alt: alternate text
            :align: center

            Permeable pavement --- porous asphalt and interlocking pavement, source: google images.

        .. _F7:
        .. figure:: _build/_images/Openpaved.jpg
            :width: 600px
            :height: 450px
            :scale: 100%
            :alt: alternate text
            :align: center

            Schematic overview of open paved (OP)

Assumptions
^^^^^^^^^^^
    * On open paved, cracks on the pavement and pores in the material that allow infiltration only occupy a very minor fraction
      of open paved surface area. Hence it does not affect the interception storage capacity on open paved surface.
    * Infiltration starts after interception storage is filled and it is limited by predefined infiltration capacity. Interception
      storage can only be emptied through evaporation.
    * There is hardly any plant under open paved area, thus no transpiration from root zone is relevant. Hence, for simplicity,
      the infiltration from open paved surface is assumed directly percolating into the groundwater (GW) without going through
      the unsaturated zone.

Calculation order
^^^^^^^^^^^^^^^^^
    * Initial interception storage on open paved at the beginning of current time step is the remaining interception storage on open paved
      at the end of previous time step plus rainfall at current time step, and it is limited by predefined interception storage capacity on open paved.
    * (Actual) evaporation from interception on open paved during current time step is limited by potential open water evaporation and available
      initial interception storage on open paved during the same time step. Evaporation is possible only if the interception storage contains water.
    * (Final) interception storage on open paved at the end of current time step is evaporation subtracted from initial interception storage.
    * The infiltration (percolation to groundwater) occurs only if interception storage gets fully filled. Infiltration is limited by predefined
      infiltration capacity on open paved. Infiltration directly flows to groundwater (GW), i.e. percolation (skipping unsaturated zone).
    * (Total) runoff from open paved during current time step is rainfall subtracting actual evaporation, the change in interception storage
      between the same time step and previous time step and percolation to groundwater. Total runoff is redistributed to the measure (Meas),
      storm water drainage system (SWDS), combined sewer system (MSS) and unpaved (UP) at predefined ratios.
    * Subtracting runoff to the measure from total runoff is the remaining runoff. Connected remaining runoff is reallocated
      to storm water drainage system (SWDS) and combined sewer system (MSS) at predefined proportions, whilst disconnected remaining
      runoff flows to unpaved area (UP) at predefined ratio.

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.openpaved
    :members:
    :undoc-members:
    :show-inheritance:

Unpaved
~~~~~~~
Unpaved is a land use type that has no hard impervious surface cover, e.g. gardens and grassland, on which the water can much
more easily infiltrate than on paved surface. Vegetation (crop) type on the unpaved area needs to be predefined. The model assumes
notable distinction between paved area (PR, CP and OP) and unpaved area (UP). On paved area, runoff is mainly drained through
the sewer system except for disconnected fraction which flows to unpaved area by assumption. However, on unpaved area, water
in the interception storage simultaneously evaporates to the atmosphere and infiltrates to unsaturated zone, and water exceeding
the interception storage capacity becomes runoff which flows to open water (OW) by assumption. Below is the schematic overview of
unpaved (see :numref:`F8`)

.. _F8:
.. figure:: _build/_images/Unpaved.jpg
    :width: 600px
    :height: 450px
    :scale: 100%
    :alt: alternate text
    :align: center

    Schematic overview of unpaved (UP)

Assumptions
^^^^^^^^^^^
    * Disconnected runoff from paved area is equally spread over the unpaved area. This runoff is added to the water
      available for infiltration and evaporation.
    * The interception capacity on unpaved area is defined as the water depth above which surface runoff generates. Interception
      capacity of vegetation is not separately defined. Evaporation by the vegetation is taken up in the transpiration from unsaturated
      zone (UZ). Evaporation and infiltration from the unpaved surface will occur as long as water remains on surface level.
    * Infiltration starts after (initial) interception storage contains water. (Initial) interception storage is proportionally
      emptied by infiltration and evaporation and excessive part from interception storage capacity becomes runoff. Infiltration is
      limited by actual infiltration capacity and available free space in root zone that allows infiltration. Evaporation is limited
      by the potential open water evaporation during that time step. (NEED MORE EXPLANATIONs!) Infiltration and evaporation happen
      simultaneously to empty initial interception storage.
    * Actual infiltration capacity during current time step is limited by the actual available free space in the root zone,
      i.e. the maximum moisture content minus the actual moisture content in root zone during the same time step. However the anticipated
      percolation from root zone to groundwater during the same time step allows more infiltration. The anticipated percolation
      is limited by the saturated permeability of the soil and the maximum moisture content minus the actual moisture content
      during that time step.  (NEED MORE EXPLANATIONS)
    * Time factor is part of the time step that water is remaining on surface level. Potential open water evaporation is multiplied
      with this time factor to get the actual evaporation on unpaved during that time step. The actual infiltration capacity
      is multiplied with this time factor to get the actual infiltration from unpaved to unsaturated zone during that time step.
    * Rainwater falling on unpaved together with runoff from disconnected paved area is first intercepted as (initial) surface
      interception storage and emptied by evaporation and infiltration, then the excessive rainwater becomes runoff. In other
      words, only rainfall exceeding the interception storage capacity runs off. Provided that a considerably large interception
      storage capacity on unpaved is predefined, there is no runoff generated.
    * Except runoff from UP to measure when defined possible, all other runoff water on unpaved flows to open water (OW) by assumption.
      If no open water area is present, the water cannot runoff and will be stored on the surface of unpaved. In that case the
      water can only evaporate or infiltrate. However, for current version Urbanwb Model, the possibility of no open water
      presence has not be fully investigated and tested. Hence, to avoid potential errors, please specify non-zero fraction
      for open water (OW).

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Total runoff from disconnected paved area to unpaved is the sum of runoff from disconnected paved area (PR, CP, OP) to
      unpaved area (UP) after conversion with the area ratio.
    * (Initial) interception storage on unpaved land at the beginning of current time step is the final remaining interception
      storage at the end of previous time step plus precipitation at current time step plus total runoff from disconnected paved
      area. It is not limited by interception storage capacity because (initial) interception storage is a transient variable
      which is only relevant in computing process.
    * (Actual) infiltration capacity during current time step is limited by predefined infiltration capacity of unpaved and available free space in
      root zone for infiltration. Available free space in root zone for infiltration is limited by maximum moisture content of the
      root zone minus moisture content of soil at previous time step plus anticipated percolation during current time step.
      Anticipated percolation is limited by saturated permeability of the soil and the difference between maximum moisture content of
      the root zone and moisture content of soil at previous time step (NEED EXPLANATIONS).
    * As stated in assumptions, time factor is part of time step that water is remaining on the surface level, besides, the water in
      the initial interception storage is emptied by evaporation and infiltration only. Hence the time factor during current time
      step is limited by 1 and the ratio of initial interception storage over the sum of potential evaporation and actual
      infiltration capacity during current time step. With time factor, actual evaporation and actual infiltration can be determined proportionally.
    * (Actual) evaporation during current time step is potential evaporation multiplied by time factor.
    * (Actual) infiltration from unpaved to unsaturated zone during current time step is actual infiltration capacity multiplied by time factor.
    * (Final) interception storage on land is limited by the predefined interception storage capacity on unpaved land and initial interception storage
      on land subtracting actual evaporation and actual infiltration.
    * (Total) runoff on unpaved land during current time step is part of the (initial) interception storage after evaporation and infiltration
      still exceeding predefined interception storage capacity on unpaved. Total runoff is redistributed to the measure (Meas)
      and open water (OW). When inflow runoff from unpaved to measure defined possible, part of runoff flows to the measure according to
      predefined ratio, whilst the rest runoff from unpaved land flows to open water (OW) by assumption.

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.unpaved
    :members:
    :undoc-members:
    :show-inheritance:

Unsaturated zone
~~~~~~~~~~~~~~~~
Underneath unpaved area (UP) is unsaturated zone (UZ). The unsaturated zone, often called the vadose zone, is the portion
of the subsurface above the phreatic table (groundwater table). Unsaturated zone below paved area (PR, CP and OP) is defined irrelevant,
thus by assumption unsaturated zone has exactly the same size as unpaved (UP). Infiltration from unpaved surface is an inflow
to unsaturated zone and deep percolation from unsaturated zone to groundwater (GW) is an outflow.
In the vadose zone, we put our focus on the root zone where the plant transpiration happens as the water uptake through plants' root
system. The root zone can be represented by means of a container in which the water content may fluctuate --- Rainfall infiltration
and capillary rise of groundwater towards root zone add water content to the root zone and decrease root zone depletion,
while soil evaporation, crop transpiration and percolation losses remove water from root zone and increase depletion [Allen]_.
Evapotranspiration from root zone is modelled as the product of reference crop evapotranspiration (using Penman-Monteith
evaporation or Makkink evaporation) and transpiration reduction coefficient. Transpiration reduction coefficient comes from
the concept of Feddes plant water stress factor in the literature [Feddes]_.

Below :numref:`F9` shows the schematic overview
of unsaturated zone. Several important definitions are recapped here. Field capacity is the amount of water that a well-drained
soil should hold against gravitational forces. In the absence of water supply, the water content in the root zone decreases
as result of water uptake by the crop. As water uptake progresses, the remaining water is held to the soil particles with
greater force, lowering its potential energy and making it more difficult for the plant to extract it. Eventually, a point
is reached where the crop can no longer extract the remaining water. The water uptake becomes zero when wilting point is
reached. Wilting point is the water content at which plants will permanently wilt.

.. _F9:
.. figure:: _build/_images/Unsaturatedzone1.jpg
    :width: 600px
    :height: 450px
    :scale: 100%
    :alt: alternate text
    :align: center

    Schematic overview of unsaturated zone

:numref:`F10` below shows how the transpiration reduction factor is related to soil water pressure head h (i.e. root zone water potential).

h = relative root zone storage = moisture content / moisture content at equilibrium.

In the range between :math:`h_3` (transpiration reduction point) and :math:`h_2` (field capacity), root water uptake is optimal (maximal),
so transpiration reduction factor (i.e. plant water stress factor) :math:`\alpha_{rw}=1`. When :math:`h < h_3`, there is
drought stress, and :math:`\alpha_{rw}` linearly reduces to zero at :math:`h_4` (permanent wilting point). When :math:`h > h_2`,
:math:`\alpha_{rw}` linearly reduces to zero at :math:`h_1` (fully saturated, i.e anoxic moisture condition).
The threshold pressure :math:`h_3` increases with potential transpiration rates, i.e. daily crop-evaporation. For low potential
transpiration rate, the threshold pressure :math:`h_{3l}` is lower than the threshold pressure :math:`h_{3h}` at high potential
transpiration rate. Computational simplifications are made here to calculate daily crop-evaporation value. Since the model is
simulated on hourly time step, for ease of computing, instead of using the sum of 24 hour crop-evaporation value to get daily crop-evaporation value,
we simply use hourly evaporation divided by :math:`2\Delta t (i.e. 2\times\frac{1}{24} d)` to represent daily potential transpiration rate
since it is assumed that crop evapotranspiration occurs only during daytime.

.. _F10:
.. figure:: _build/_images/transpiration.jpg
    :width: 600px
    :height: 300px
    :scale: 100%
    :alt: alternate text
    :align: center

    Transpiration reduction coefficient in Urbanwb (i.e. plant water stress factor) in relation to root zone water potential, graph copied from literature [Dejongvanlier]_


Some easily-confused concepts regarding evapotranspiration, mostly from `Food and Agriculture Organization of the United Nations (FAO)`_ and other referenced sources:
    * Evapotranspiration: Evapotranspiration is an important component of the water cycle and is composed of two-subprocesses:
      evapotration from soil and vegetation surfaces and transpiration from plant through root-stomata system. Evaporation and
      transpiration occur simultaneously and there is no easy way of distinguishing between the two processes.
    * Reference crop evapotranspiration :math:`ET_{0}`: The evapotranspiration rate from a reference surface, not short of water, is called reference
      crop evapotranspiration or reference evapotranspiration and is denoted as :math:`ET_{0}`. The reference surface is a hypothetical
      grass reference crop with an assumed crop height of 0.12 m, a fixed surface resistance of 70 s/m and an albedo of 0.23.
      As a result of an Expert Consultation held in May 1990, the  FAO Penman-Monteith method is recommended as the sole standard
      method for the definition and computation of the reference crop evapotranspiration method for determining :math:`ET_{0}`.
      :math:`ET_{0}` can also be estimated from pan evaporation. Pans have proved their practical value and have been used
      successfully to estimate :math:`ET_{0}` by observing the water loss from the pan and using empirical coefficients to
      relate pan evaporation to :math:`ET_{0}`. However, special precautions and management must be applied. Besides, Makkink evapotration
      commonly used in the Netherlands can be used to estimate :math:`ET_{0}` as well. Makkink evapotration = 0.8982 * Penman
      Montieth evapotration according to [STOWA]_.
    * Crop evapotranspiration under standard conditions :math:`ET_{c}`: The crop evapotranspiration under standard conditions,
      denoted as :math:`ET_{c}`, is the evapotranspiration from disease-free, well-fertilized crops, grown in large fields,
      under optimum soil water conditions, and achieving full production under the given climatic conditions.
      :math:`ET_{c}=K_{c}ET_{0}`.

      :math:`K_{c}` is crop factor (crop coefficient). The effect of both crop transpiration and soil evaporation are integrated
      into this single crop coefficient :math:`K_{c}`. :math:`K_{c}` varies with crop type, growth stage and other factors,
      the range of which is commonly (:math:`0.2 < K_{c} < 1.3`). For simplicity, we say that crop factor :math:`K_{c}=1`
      for hypothetical grass reference crop.
    * (Actual) evapotranspiration :math:`ET` : As stated above, the :math:`ET` from crop surfaces under standard conditions is
      determined by crop coefficient :math:`K_{c}` that relate :math:`ET_{c}` to :math:`ET_{0}`. However actual evapotranspiration
      is usually under non-standard conditions. The :math:`ET` from crop surfaces under non-standard conditions is adjusted
      by a water stress coefficient (:math:`\alpha`) and/or by modifying the crop coefficient. Hence, the (actual) evapotranspiration
      is :math:`ET=\alpha*K_{c}*ET_{0}`. In Urbanwb model, we take 1.0 for crop factor, Penman-Monteith evaporation (or Makkink evapotration)
      for reference crop evapotranspiration, transpiration reduction factor as water stress factor, so the modelled
      evapotranspiration is :math:`ET= \alpha*1*E_{PM}`.
    * Makkink evapotranspiration: Though Penman-Monteith method is solely recommended by FAO to calculate reference crop
      evapotranspiration and has been commonly used world-widely, there are several other methods popular in certain area or nations.
      Makkink method is named after Gerrit François Makkink, a Dutch hydrologist [Makkink]_. Makkink method is simple but must
      be calibrated to a specific location. Since 1987, KNMI used Makkink method as standard method to calculate reference crop
      evapotranspiration. Hence, Makkink evaporation can be used as the forcing "reference crop evapotranspiration"
      in replace of Penman-Monteith evaporation, especially for study cases in the Netherlands. The relationship between
      Makkink evaporation and Penman-Monteith evaporation is Makkink evapotration = 0.8982 * Penman Montieth evapotration according to [STOWA]_.

Assumptions
^^^^^^^^^^^
    * Infiltration from open paved surface (OP) percolates directly to groundwater (GW) without passing unsaturated zone. Unsaturated zone
      is only relevant beneath unpaved area. The area of unsaturated zone is equal to area of the unpaved area.
    * Since the model is evaluated on hourly time step (currently), for computing simplicity, hourly reference crop evapotranspiration is
      divided by :math:`2\Delta t` to get the daily crop-evaporation value as the potential transpiration rate that determines the
      transpiration reduction point :math:`h_{3}`. The reason for diving :math:`2\Delta t` is it is assumed that (crop-)evaporation
      occurs only during daytime (half a day). Actually, it would be better to apply the sum of hourly reference crop evapotranspiration
      for 24 time steps within that day as the daily crop evaporation value, but for the sake of computing efficiency and robustness,
      we use this simplification and we argue this simplification is a good approximation and has negligible impacts on computed results. (REALLY?)
    * (Actual) evapotranspiration during current time step is determined by transpiration reduction factor (water stress factor)
      and reference crop evapotranspiration during the same time step (crop factor =1).
    * Percolation to groundwater is limited by the saturated conductivity of the soil.

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Total infiltration from unpaved area is taken as the influx.
    * Calculate runoff from measure to unsaturated zone if defined possible.
    * Calculate moisture content of soil in the root zone at transpiration reduction point :math:`\theta_{h3}`.
      If daily reference evapotranspiration is less than 1 mm/d, :math:`\theta_{h3} = \theta_{h3l}`.
      If daily reference evapotranspiration is more than 5 mm/d, :math:`\theta_{h3} = \theta_{h3h}`.
      If daily reference evapotranspiration is between 1 mm/d and 5 mm/d, :math:`\theta_{h3}` is interpolated between :math:`\theta_{h3l}`
      and :math:`\theta_{h3h}`.
    * Determine transpiration reduction factor :math:`\alpha` by linear interpolation between :math:`\theta_{h1}` (moisture
      content of root zone at complete saturation point), :math:`\theta_{h2}` (moisture content of root zone at field capacity)
      , :math:`\theta_{h3}` (moisture content of root zone at transpiration reduction point), and :math:`\theta_{h4}` (moisture
      content of root zone at permanent wilting point), based on actual moisture content of root zone at previous time step plus
      the infiltration from unpaved area during current time step.
    * Evapotranspiration from unsaturated zone during current time step is the product of transpiration reduction factor :math:`\alpha` and
      reference crop evapotranspiration :math:`ET_{0}` during the same time step.
    * Determine equilibrium root zone moisture content :math:`\theta_{eq}` by interpolation, based on the groundwater level
      at previous time step. In database, for given soil type and crop type, we have information on equilibrium mositure
      content of root zone for different groundwater levels (from 0 to 10 m-SL). Hence, the equilibrium moisture content of
      root zone during current time step :math:`\theta_{eq}` is interpolated from the lookup table based on the groundwater
      level at previous time step.
    * Determine maximum capillary rise by interpolation, based on the groundwater level at the previous time step. In database,
      for given soil type, we have information on maximum capillary rise for different groundwater levels (from 0 to 10 m-SL).
      Similarly to calculating equilibrium moisture content of root zone, the maximum capillary rise during current time step
      is interpolated from the lookup table based on the groundwater level at previous time step.
    * Determine percolation from unsaturated zone (UZ) to groundwater (GW). It can be positive (downward deep percolation) and negative
      (upward capillary rise). Note that deep percolation to groundwater and capillary rise from water table are summarised into one
      term in Urbanwb model.
      If current root zone water budget (root zone moisture content at previous time step + infiltration from UP +
      runoff from measure to UZ - evapotranspiration) is greater than equilibrium root zone moisture content :math:`\theta_{eq}`,
      it is downward deep percolation, otherwise it is upward capillary rise. Deep percolation is limited by saturated
      permeability of the soil and difference between current water budget and equilibrium root zone moisture content :math:`\theta_{eq}`;
      Capillary rise is limited by maximum capillary rise and different between current water budget and equilibrium root zone moisture content :math:`\theta_{eq}`.
    * Determine moisture content of root zone :math:`\theta` at the end of current time step. The root zone moisture content at
      the end of current time step is the root zone moisture content at the end of previous time step + infiltration + runoff from measure -
      evapotranspiration - percolation, which values are all calculated above.

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.unsaturatedzone
    :members:
    :undoc-members:
    :show-inheritance:

Groundwater
~~~~~~~~~~~
In the Urbanwb Model, underneath the unsaturated zone is the saturated zone, i.e. (shallow) groundwater reservoir (GW).
Groundwater reservoir is modelled as an unconfined aquifer which consists of a pervious layer underlain by a (semi-)impervious
layer. Below this (semi-)impervious aquitard is one of the exchanges of the Urbanwb Model --- deep groundwater reservoir
(deep GW). Percolation from unsaturated zone and open paved recharges the groundwater, while downward seepage to deep groundwater
and drainage (seepage) to open water deplete groundwater stock. The inflow (percolation from unsaturated zone) and outflow (seepage
and draiange) are driven by the head difference, so the value of these fluxes can be positive or negative. Below :numref:`F11` shows
the schematic overview of groundwater reservoir. Area of groundwater reservoir (GW) is calculated as the area of the total
model - area of open water fraction that is not above the groundwater level - area of paved roof fraction of which the basement
is below groundwater. Maximum capillary rise and storage coefficient during current time step are determined by interpolation
based on groundwater level at previous time step.

.. _F11:
.. figure:: _build/_images/groundwater1.jpg
    :width: 600px
    :height: 450px
    :scale: 100%
    :alt: alternate text
    :align: center

    Schematic overview of groundwater reservoir

The formula of groundwater level during current time step :math:`h(t)` and its derivation are shown below. In :numref:`F12`, P is percolation, :math:`Q_s=\frac{H-h}{vc}`
is seepage to deep groundwater, :math:`Q_{d}=\frac{pp-h}{w}` is drainage to open water. All relevant levels are relative to the surface level, the unit (m-SL)
means meter below surface level.


.. _F12:
.. figure:: _build/_images/groundwater_illu.jpg
    :width: 700px
    :height: 300px
    :scale: 100%
    :alt: alternate text
    :align: center

    Groundwater level h(t) calculation

.. math::

    \because \frac{dh(t)}{dt} = \frac{Q_{in}}{\mu}=\frac{Q_s(t)+Q_d(t)+P}{\mu} = \frac{\frac{H-h(t)}{vc}+\frac{pp-h(t)}{w}+P}{\mu} \\
     = \frac{H\cdot w+pp\cdot vc+P\cdot vc\cdot w}{\mu \cdot vc\cdot w} - \frac{w+vc}{\mu\cdot vc\cdot w}h(t)

    \therefore \frac{\mu\cdot vc\cdot w}{w+vc}\cdot \frac{dh(t)}{dt}=\frac{H\cdot w+pp\cdot vc+P\cdot vc\cdot w}{w+vc} - h(t)

    \because A\cdot \frac{dx}{dt} = B - x \Rightarrow x=K_1 e^{-\frac{t}{A}}+B

    t = 0 \Rightarrow h(t) = h_0 = K_1 + B

    \because A = \frac{\mu\cdot vc\cdot w}{w+vc}, B = \frac{H\cdot w+pp\cdot vc+P\cdot vc\cdot w}{w+vc}

    \therefore h(t) = B + (h_0 - B)\cdot e^{-\frac{t}{A}}

    \therefore h(t) = \frac{H\cdot w+pp\cdot vc + P\cdot vc\cdot w}{w+vc}+(h_0 - \frac{H\cdot w+pp\cdot vc+P\cdot vc\cdot w}{w+vc})\cdot e^{-t\cdot \frac{w+vc}{\mu\cdot w\cdot vc}}

Assumptions
^^^^^^^^^^^
    * The infiltration water from open paved flows directly to groundwater (percolation) without passing unsaturated zone.
    * The area of groundwater reservoir is equal to the total area - part of the surface water area below phreatic table -
      part of the paved roof area of which the basement is below groundwater.
    * Drainage and seepage are calculated based on the groundwater level at the end of previous time step. Drainage and seepage
      are reduced due to the changing groundwater level caused by the fluxes. It means higher the head difference
      between shallow groundwater and deep groundwater (or open water), higher the driving force, greater the flux.
      With water exchanging, head difference gets smaller, so the flux gets smaller.

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Percolation to groundwater is the sum of percolation from open paved and percolation from unsaturated zone converted
      with the area ratio.
    * Calculate runoff from measure to groundwater reservoir if defined possible.
    * Determine storage coefficient :math:`\mu` by interpolation, based on the groundwater level at the previous time step.
      In database, for given soil type, we have information on storage coefficient for different groundwater levels (from 0 to 10 m-SL).
      The storage coefficient of groundwater during current time step is interpolated from the lookup table based on the groundwater
      level at previous time step.
    * Determine groundwater level during current time step at current time step based on the calculation formula mentioned above.
    * Determine seepage to deep groundwater (positive: downward, negative: upward) during current time step based on predefined
      seepage. Seepage to deep groundwater can be defined either as a constant flux (0:flux) or a dynamically-computed flux (0:level)
      which depends on predefined hydraulic head of deep groundwater and vertical drainage resistance :math:`vc` between (shallow)
      groundwater (GW) and deep groundwater.
    * Determine drainage from groundwater reservoir to open water during current time step based on water balance.
      Note here the drainage calculation is irrelevant to drainage resistance :math:`w`, only related to water balance.
      Drainage resistance :math:`w` is only relevant in groundwater level :math:`h(t)` calculation.
    * Determine groundwater level below surface level and groundwater above surface level at the end of current time step.
      They are dependent on groundwater level at the end of previous time step, and calculated percolation, seepage, drainage
      flux and storage coefficient :math:`\mu` during current time step. (NEED EXPLANATIONS on h(t) and gwl)


Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.groundwater
    :members:
    :undoc-members:
    :show-inheritance:

Sewer system
~~~~~~~~~~~~
Sewer system in Urbanwb model is the combination of storm water drainage system (SWDS) and combined sewer system (MSS), the proportion and
system capacity of which should be predefined according to the local context. Combined sewer system is abbreviated as MSS here since
mixed sewer system is also a frequently-used jargon by the model developer. During dry flow condition, all water in combined
sewer system (MSS) is transferred to waste water treatment plant (WWTP) for further treatment. During wet flow condition
(e.g. heavy storms), the relief structure CSO weir allows major part of the combined stormwater and sewage to be discharged
untreatedly to an adjacent water body. Combined sewer system has two phases during wet flow condition: In phase one, combined
sewer system collects water from paved areas and discharges it together with the sewage to waste water treatment plant (WWTP),
and the system gets filled before sewer overflow through CSO weir to open water occurs. If the rainfall event is heavier,
combined sewer system enters phase two --- combined sewer overflow occurs, which may impose pollution problem to receiving water body.
However, if the combined sewer overflow discharge capacity is still exceeded due to very extreme rainfall, then the sewer
overflow onto the street will occur. In contrast to combined sewer system (MSS), Storm water drainage system (SWDS) separating
stormwater with sewage to avoid pollution, drains stormwater directly to surface water, limited by predefined system discharge
capacity above which the sewer overflow onto the street will occur. The schematic overview of sewer system is clear in :numref:`F1`.

Assumptions
^^^^^^^^^^^
    * Discharge capacity of sewer system cannot be directly defined in the configuration file. Since the Urbanwb model is
      originally developed on the basis of study cases in the Netherlands, there are some localized settings for ease of use.
      Hence it is user's responsibility to understand the model and tailor the input for more realistic modelling of their interest.
      System discharge capacity of storm water drainage system (SWDS) and combined sewer system (MSS) are derived based on the
      rainfall intensity (T=2year, T=1/6year) and predefined sewer system storage capacity. In the Netherlands, the combined
      sewer overflow is designed to occur 6 times per year, so the combined sewer system discharge capacity to WWTP above
      which the sewer overflow occurs is calculated as rainfall intensity (T=1/6year) - storage capacity of combined sewer system
      (2mm). The sewer overflow through manhole onto the street is designed to occur once every two year, so the sewer system
      discharge capacity to open water above which the sewer overflow onto the street occurs is calculated as rainfall intensity
      (T=2year) - storage capacity (SWDS:9mm, MSS:2mm). Some detailed explanations can be found in the parameter estimation section.
    * Area of sewer system is equal to the total area of paved areas (PR, CP, OP) that is connected to the sewer system. Area of
      storm water drainage system and area of combined sewer system are determined by predefined ratios. Runoff from paved
      areas to sewer system is partitioned to combined sewer system and storm water drainage system at these predefined
      ratios. It means, for example, Area A has 60% SWDS and 40% MSS, then 60% of the runoff from the paved roof (no measure applied)
      will be drained to SWDS, not 30%.

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Determine total runoff from paved areas (PR, CP, OP) and measure (if defined possible) to storm water drainage system
      (SWDS) during the current time step converted with area ratio.
    * Determine total runoff from paved areas (PR, CP, OP) and measure (if defined possible )to combined sewer system (MSS)
      during the current time step converted with area ratio.
    * Determine outflow from storm water drainage system (SWDS) to open water (OW) during current time step based on storage in SWDS
      at previous time step, runoff from paved areas and measure. Outflow from SWDS to surface water is limited by the discharge
      capacity of the storm water drainage system --- the storm water drainage capacity to open water above which water will overflow
      onto the street. In the Netherlands, sewer overflow onto the street is designed to occur once every two year.
    * Determine outflow from combined sewer system to waste water treatment plant during current time step which is limited by
      the discharge capacity of the combined sewer system to WWTP --- the combined sewer discharge capacity above which combined sewer
      overflow to open water will occur. In the Netherlands, combined sewer overflow is designed to occur six to seven times a year.
    * Determine outflow from combined sewer system to open water during current time step which is limited by the discharge
      capacity of the combined sewer system to open water --- the combined sewer discharge capacity above which overflow onto
      the street will occur. In the Netherlands, sewer overflow onto the street is designed to occur once every two year.
    * Determine sewer overflow onto the street from storm water drainage system (SWDS) during current time step. Overflow water is
      drained at the same time step to open water by assumption.
    * Determine sewer overflow onto the street from combined sewer system (MSS) during current time step. Overflow water is drained
      the same time step to open water by assumption.
    * Determine storage in the storm water drainage system (SWDS) at the end of current time step. Storage is only used when the
      discharge capacity is exceeded by the inflow volume. Storage is limited to the storage capacity. All other excess
      water will result in overflow.
    * Determine storage in the combined sewer system (MSS) at the end of current time step. Storage is only used when the
      discharge capacity is exceeded by the inflow volume. Storage is limited to the storage capacity. All other excess
      water will result in overflow.

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.sewersystem
    :members:
    :undoc-members:
    :show-inheritance:

Open water
~~~~~~~~~~
Open water in the Urbanwb model refers to all control open water bodies, e.g. ditches, canals and ponds in a polder system.
Open water can be deemed as an abstract term reflecting system storage capacity.
By assumption, runoff from unpaved and sewer overflow onto the street flow to the open water. Sewer system outflow and groundwater
drainage recharge the open water. A target open water level is set as reference water level, for example 1.5 meter below
surface level (1.5 m-SL). Excess water above the target level gets pumped to outside limited by certain discharge capacity
to try to maintain this level, evaporation loss is compensated by the recharge from outside water. This target level is
assumed to be the lowest open water level (down limit). During simulation, under successive heavy rain events, open water
level may exceed the target level due to insufficient storage capacity and discharge capacity, indicating there is excessive
water the water system cannot handle, which represents all kinds of real urban flood phenomenons. Hence, we calculate
storage height above the target open water level to understand the storage requirements of the water system. Maximum storage height
on open water  for a certain flood event averaged over the entire study domain reflects the required storage capacity in depth
for the total study area during that event. To sum up, open water component is an abstract recipient water body that indicates
the required storage capacity of the system. Schematic overview of Open water is in :numref:`F13`

.. _F13:
.. figure:: _build/_images/openwater.jpg
    :width: 600px
    :height: 450px
    :scale: 100%
    :alt: alternate text
    :align: center

    Schematic overview of open water

Assumptions
^^^^^^^^^^^

    * Runoff from the unpaved flows to the open water during the same time step.
    * Sewer overflow onto the street from the storm water drainage system (SWDS) and combined sewer system (MSS) flows
      directly to the open water.
    * Target open water level is defined as the level below the surface level. It is the lower limit of the open water level.
      For instance, the target open water level is set 1.5 m-SL, then the computed open water level x can only be higher than
      this level (x <= 1.5). Above this level (x < 1.5), discharge from open water to outside water starts (discharge from
      model inner to outer). The outside water is not part of the model, and discharge from open water to outside is limited
      by a predefined pumping capacity. This pumping capacity is the Q in the Storage-discharge-frequency (SDF) Curve.

Calculation orders
^^^^^^^^^^^^^^^^^^

    * Determine direct rainfall and evaporation on open water during current time step.
    * Determine total runoff from unpaved area to open water during current time step.
    * Determine drainage from groundwater to open water during current time step.
    * Determine total outflow from sewer systems to open water during current time step.
    * Determine total sewer overflow onto the street from sewer systems to open water during current time step.
    * Determine inflow from measure (if applicable) to open water during current time step.
    * Determine discharge from open water to outside water during current time step.
    * Determine open water level at the end of the current time step.


Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: urbanwb.openwater
    :members:
    :undoc-members:
    :show-inheritance:


Measure
~~~~~~~
Urban flooding are usually attributed to three types: pluvial flooding, fluvial flooding and coastal flooding. Pluvial flooding occurs
when an extremely heavy rainfall saturates storage capacity of the water system and excess water cannot be absorbed. Fluvial flooding
occurs when rivers burst their bank as a result of sustained or intense rainfall. Coastal flooding occurs in coastal area as a result
of extreme tidal conditions like storm surges. Unlike other types of flooding, pluvial flooding is a direct, quick and localized
consequence of rainfall, and it is a predominantly urban phenomenon as it is in urban area where the effects are most pronounced and
damaging [Susana]_. Urbanwb model simulates only the pluvial flooding in urban water systems through two indicators --- sewer overflow onto
the street and storage height above the target open water level. Climate changing increasing the intensity and frequency of extreme rainfall events
, together with rapid growing urbanisation and population, may result in increased urban pluvial flood risks. To effectively
adapt with rising flooding risk, a combination of intervention strategies is required, including structural infrastructure, nature-based
solutions, early warning system, risk financing instrument and etc. Urbanwb is capable of modelling physical adaptation
measures. Physical measures can be categorized into artificial structural infrastructure and nature-based solutions. Structural infrastructure
refers to gery infrastructure which are engineering projects that use concrete and steel, while nature-based solutions refer to
green infrastructure that depend on plants and ecosystem services (they may be totally constructed artificially). Green infrastructure
is the strategic use of networks of natural lands, working landscapes, and other open spaces to conserve ecosystem values
and functions and provide associated benefits to human populations according to [Benedict]_. Blue-green infrastructure is also
a term used interchangeably with green infrastructure. Green infrastructure is generally decentralized ---
water is captured and treated where it falls, rather than being transported to a treatment facility. Green infrastructure terminology
can also be used in the context of low impact development (LID). Grey infrastructure refers to the human-engineered infrastructure
for water resources such as water and wastewater treatment plants, pipelines, and reservoirs. Grey infrastructure typically
refers to components of a centralized approach to water management.
Examples of grey infrastructure are canal, levees, ditches, raised curb, underground off-line tank and etc.
Examples of green infrastructure are rainwater harvesting, urban wetlands, green roof, bioswale and etc.
A module named Measure is creatively developed by Toine in Urbanwb model to model the physical urban adaptation measures.
With the ingenious setup of this module, underlying mechanisms of these physical measures are simulated and incorporated into
the dynamics of the entire modelling of water system. Next paragraphs provide detailed descriptions on the structure of the Measure module.

Measures mitigate urban flooding by means of creating extra storage, encouraging evapotranspiration, facilitating infiltration,
increasing drainage and the combination of these interventions. Consequently, despite many types/terms of urban adaptation measures,
they can be categorised and modelled under certain framework with specific settings. This is the underlying idea and fundamental
principle of this Measure module --- to propose a general adaptive framework that represents measures' physical dimensions and
mimics measures' predominant functionality.

Measure in Urbanwb model can be defined as 1-layer, 2-layer or 3-layer structure (see :numref:`F14`).  1-layer structure contains only interception layer (layer no. 1),
which can represent type of measure that creates storage and allows evaporation, a typical example would be a blue roof.
2-layer measure structure consists of 2 layers --- interception layer (layer no. 1) and bottom storage layer (layer no.3). Bottom storage layer
is the most sophisticated part of measure module. In the bottom storage layer, evapotranspiration, percolation to groundwater,
controlled runoff can be defined by the user. Controlled runoff means the runoff that is first controlled by the measure and then evaporated, immediately pumped
or delayed drained to somewhere else, so controlled runoff is no longer a problem in terms of the area where the measure is applied.
Controlled runoff can be defined either as a constant flux or a dynamically-computed flux that dependents on the head difference and
resistance. Percolation to groundwater from the bottom storage layer of measure can be defined either as the percolation
limited by saturated permeability of soil or can be defined as a kind of delayed drainage controlled runoff to simulate
the water jamming/logging effect that hampers the free percolation to groundwater from measure. Hence, the setup of the measures
involves expert judgement, the model is as good as the modeller. Examples of 2-layer measures are rain barrel, wet pond,
infiltration box and etc. 3-layer measure structure comprises 3 layers - interception layer (layer no. 1), top storage layer
(layer no. 2) and bottom storage layer (layer no.3). Extra top storage layer in 3-layer measure is especially added to
model measures like green roof and bioswale. These measures have growing medium that encourages evapotranspiration and
a drainage layer beneath growing medium that drains excessive water to sewer system. Some examples are provided in next paragraph
to inspire the user how to conceptualise a measure into this Measure module.

.. _F14:
.. figure:: _build/_images/measure_layers.jpg
    :width: 600px
    :height: 200px
    :scale: 100%
    :alt: alternate text
    :align: center

    Layer of measure

**Some examples of how to conceptualise measures for user's ease of use**:

**Blue roof**:
Blue roof (without drainage) is creating extra storage on building roof that allows evaporation. Blue roof is a storage installation. In fact, it can be modelled
with basic model or with Measure module. Model a blue roof with basic model is to simply change the interception capacity on paved roof.
To model a blue roof with Measure module, a blue roof can be conceptualised as a simple 1-layer structure --- only the interception
layer with certain storage capacity where evaporation is allowed. The storage in a blue roof can be emptied only through evaporation.
Overflow from blue roof will be drained to the SWDS.

**Wet pond**:
:numref:`F15` shows the schematic view of how wet pond is conceptualised. An artificial wet pond can be thought as a 2-layer structure --- the interception layer is a pseudo layer that has no storage
capacity and infinite infiltration capacity, so all water (precipitation and inflow runoff from contributing area) penetrates
interception layer directly into the bottom storage layer. A wet pond usually has a sealed concrete bottom to ensure permanent
pool thus percolation is defined impossible. Wet pond has a drainage level above which the excess water is drained to SWDS,
and this runoff is called controlled runoff. Higher the head difference, quicker it drains, besides, a drainage resistance needs to be
defined by the user to determine how quick it drains. We assume the initial storage of a wet pond is not empty and set as
drainage level, thus a initial value for bottom storage layer of measure should be defined .Evaporation from the pool is possible and is limited by Penman evaporation.
When there is very extreme rainfall event, incoming runoff may fully fill the storage capacity of wet pond, so the overflow from wet pond occurs.
Unlike controlled runoff from bottom storage layer, this overflow is an uncontrolled runoff, and will be drained eventually to SWDS.
Uncontrolled runoff is problematic thus is often of interest to user. By comparing the time series of uncontrolled runoff with
the time series of baseline runoff, we can get an idea of the normative runoff reduction of the measure for measure inflow area.

.. _F15:
.. figure:: _build/_images/wetpond.jpg
    :width: 600px
    :height: 200px
    :scale: 100%
    :alt: alternate text
    :align: center

    Conceptualisation of wet pond, figure on left panel from [LID]_.

**Bioswale**
:numref:`F16` shows the schematic view of how bioswale is conceptualised. A bioswale is a infiltration installation. An bioswale can be thought as a 3-layer structure ---
surface vegetated soil as the interception layer which provides limited storage capacity and facilitates infiltration to the
growing medium. Growing medium is the top storage layer where plant transpiration and soil evaporation happens. After evapotranspiration,
excessive water infiltrates into the bottom drainage layer. Below the growing medium is the gravel drainage layer encouraging water
percolating into the groundwater reservoir. Here the percolation flux can be modelled either as percolation to groundwater
limited by saturated permeability of soil, or as a controlled runoff to groundwater dependent on predefined drainage level and resistance
to mimic the water jamming. Definition is up to the user after considerable thoughts. Evaporation from the bottom drainage layer is possible when potential evapotranspiration rate exceeds the
transpiration from growing medium (top storage layer) because root can uptake water from drainage layer for further transpiration.
Overflow from the bottom drainage layer (bottom storage layer) and surface overflow from interception layer are uncontrolled runoff,
which will be drained to SWDS. As said above, total uncontrolled runoff to SWDS is in this case of users' interest.
Similar to bioswale, green roof is also modelled as a 3-layer structure, however, there are two
major difference: 1. Green roof is installed on the building roof, thus controlled runoff directs to the SWDS instead of GW.
2. Calculation formula for green roof is specifically modified to make sure no surface submergence from green roof is possible
because a normally-functioning green roof should has no water logging on the surface. Please remember to modify the measure type ("greenroof type")
in the measure configuration file when modelling green roof-alike measure. Besides, the user should pay attention to the difference between
measure design dimension and actual storage capacity (depth) used in the model. The difference between the two is the multiplication
of void ratio. For void storage space, like water square or wet pond, the void ratio is 1.0; for growing medium, gravel and etc, the void ratio
should be say 0.3. Percolation to groundwater limited by the groundwater level can be define possible in Urbanwb. However, that
function has not be tested and further developed thus it is not recommended to use that setting.

.. _F16:
.. figure:: _build/_images/bioswale.jpg
    :width: 600px
    :height: 200px
    :scale: 100%
    :alt: alternate text
    :align: center

    Conceptualisation of bioswale, figure on the left panel from [LID]_.


Assumption
^^^^^^^^^^
    * A measure can be defined as 3-layer. Even though the area of each layer of measure can be defined different, it is
      not recommended to do so because it has not been fully tested.
    * Measure inflow area does not necessarily comes from one source. For instance, a measure is defined at OP area, it is
      possible to define measure inflow area not only from OP area but also from PR and CP area. However, the possibilities
      have not been fully developed and tested. It's users' responsibility to pay attention to the boundary condition of the model.
    * Not all the measure can be implemented with Measure module or implemented with the Urbanwb model. User should understand
      the correct way of using this Urbanwb model and be careful with the limitations and potential bugs in this model.

Calculation orders
^^^^^^^^^^^^^^^^^^
    * Determine rainfall on the measure during current time step.
    * Determine runoff from measure inflow area to measure during current time step.
    * Determine initial interception storage on interception storage of measure. Initial interception water budge includes
      interception storage at the end of previous time step + rainfall + runoff from measure inflow area if runoff is defined
      directed to interception layer.
    * Determine evaporation from interception layer of measure, limited by Penman evaporation.
    * Determine downward infiltration from interception layer. Downward infiltration from interception layer only possible when
      measure structure contain at least 2 layers. Downward infiltration calculation for green roof is separately defined.
    * Determine surface overflow from interception layer of measure.
    * Determine final interception storage on interception layer of measure.
    * Determine initial storage in top storage layer of measure. When measure structure contains only 2 layers. This storage is
      zeros (when 2 layer --- no top storage layer is involved, all the variable related to top storage layer will be zero.)
      When 3 layer, initial storage in top storage layer of measure is storage at previous time step + downward infiltration from
      interception layer.
    * Determine transpiration from top storage layer of measure, limited by water availability and Penman evaporation multiplied
      with a predefined reduction factor.
    * Determine percolation from top storage layer of measure to bottom storage layer of measure. This variable is separately
      defined for green roof type measure.
    * Determine final storage in top storage layer of measure, limited by predefined storage capacity of top storage layer of measure.
    * Determine initial storage in bottom storage layer of measure.
    * Determine evapotranspiration from bottom storage layer of measure. Transpiration from bottom storage layer only when defined
      possible and when transpiration capacity exceeds transpiration from top storage layer when there is 3 layers.
    * Determine percolation from bottom storage layer of measure to groundwater. Need to specify whether this percolation is
      limited by groundwater level. If not, the limitation will only be the saturated permeability. It is recommended to
      specify percolation not limited by groundwater level.
    * Determine controlled runoff from bottom storage level of measure. The controlled runoff can be modelled as either a constant flux
      or as a dynamically-computed flux that depends on the drainage level and resistance.
    * Determine final storage of bottom storage layer of measure.
    * Determine overflow from bottom storage layer of measure if bottom layer is completely filled.
    * Determine outflow from measure to OW, UZ, GW, SWDS, MSS, Out

Code and input arguments
^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: urbanwb.measure
    :members:
    :undoc-members:
    :show-inheritance:

FAQ
---
1. What is area of xx with measure, area of xx without measure, measure inflow area from xx?
    .. _F17:
    .. figure:: _build/_images/areas.jpg
        :width: 350px
        :height: 220px
        :scale: 100%
        :alt: alternate text
        :align: center

        Illustration of measure inflow area

    * For individual component of simulation model, though we call it PR, OP and etc in the documentation, actually
      in calculation it is area of PR, OP and etc without measure other than total area of PR, OP and etc. As you can see in
      :numref:`F17`, we take applying measure on Open paved as an example. The measure area is 2 m2, and the total open paved area
      is 10 m2, when measure is applied on Open paved, the area of open paved with measure is 2 m2, the area of open paved without
      measure is 10-2= 8 m2. Measure inflow area from OP should be always larger than the measure area (and area of open paved with measure)
      and limited by the total open paved area. Of course, total measure inflow area can be larger than the total open paved area
      as long as it has measure inflow area from other land cover say e.g paved roof.
    * If no measure is applied or runoff inflow area from OP to measure equals to measure area (i.e. area of OP with measure),
      then there is no runoff inflowing from open paved area without measure to the measure. Inflow factor is calculated as
      (the measure inflow area from xx - area of xx without measure) / area of xx with measure, to determine how much percentage
      of runoff from area of xx without measure flows to the measure.

Parameter estimation
--------------------

References
----------
.. [Penman] Penman, H. L. (1948). Natural evaporation from open water, bare soil and grass. Proceedings of the Royal Society of London. Series A. Mathematical and Physical Sciences, 193(1032), 120-145.
.. [Monteith] Monteith, J. L. (1965, July). Evaporation and environment. In Symp. Soc. Exp. Biol (Vol. 19, No. 205-23, p. 4).
.. [Feddes] Feddes, R.A., Kowalik, P.J., Zaradny, H., (1978). Simulation of filed water use and crop yieldSimulation Monographs. Pudoc, Wageningen, 189pp
.. [Dejongvanlier] DE JONG VAN LIER, Q., et al (2008). Macroscopic root water uptake distribution using a matric flux potential approach. Vadose Zone Journal, 2008, 7.3: 1065-1078.
.. [Allen] Allen, R.G., Pereira, L.S., Raes, D., and Smith, M. 1998. Crop evapotranspiration: Guidelines for computing crop water requirements. FAO Irrigation and DrainagePaper No. 56, United Nations, FAO, Rome, Italy.
.. [STOWA] STOWA, 2009 rapport 11. VERBETERING BEPALING ACTUELE VERDAMPING VOOR HET STRATEGISCH WATERBEHEER. isbn 978.90.5773.428.1
.. [Makkink] Makkink, G. F. (1957). Testing the Penman formula by means of lysimeters. Journal of the Institution of Water Engineerrs, 11, 277-288.
.. [Susana] Urban pluvial flooding and climate change: London (UK), Rafina (Greece) and Coimbra (Portugal)
.. [Benedict] Benedict, M. A., & McMahon, E. T. (2006). Green infrastructure. Island, Washington, DC.
.. [LID] Low impact development --- a design manual for urban areas
.. _Food and Agriculture Organization of the United Nations (FAO): http://www.fao.org/docrep/X0490E/x0490e04.htm#TopOfPage