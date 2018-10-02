Running the model
=================

Overview
~~~~~~~~

In general the model is run from the windows command line or bat file. It is highly recommended for now to use bat.file.
For the time being, the most commonly used function is ``savecsv`` and ``batch-run-sdf``.

The ``running_sample`` folder in the package includes the sample of running the model for both basic model and model with measure.
The model with measure is still under development. It is recommended you for the time being add you running scripts in this folder.

There are two input to run the model:

``Dynamic input``: The forcing --- Hourly time series of Precipitation, potential open water evaporation and potential reference crop evaporation
(0.8982 * Penman evaporation). The user is responsible for data preprocessing --- clean data, replace vacant data, remove
unrealistic data and make sure the data is float type (We are considering to include automatically change to float type for user, but it is not
relevant for now). Make sure the column name is the same because script use the column name to know which is precipitation and evaporation.

``Static input``: All the static parameters in the configuration file ``.ini``. We have two static input file, one is only for the basics of model (stat1),
the other is for the measure. If no measure is modelled, please specify ``choice=0`` in static input file for the measure (stat2).
Please modify the parameters according to your area of interest.

Input and parameter explanation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

a. Dynamic input
^^^^^^^^^^^^^^^^
Forcing: Hourly time series of precipitation (actually only rainfall) [mm] and potential evaporation of
open water [mm]. Length should better be most recent 30 years. Atmosphere is the most
crucial exchange to the model.
1. Format:
CSV format is preferred with corresponding column names. Make sure the data has no vacancy or unrealistic data. Make sure
the data is in float type.
2. Note:
Sometimes hourly potential open water evaporation is not findable, and it may be easier to
get access to data like class-A pan evaporation time series. However, pan evaporation
cannot be used as input directly. Conversion from pan evaporation to Penman open water
evaporation should be done before running the model.
Sometimes it is possible that only daily evaporation time series is available or even daily
evaporation time series is not available, then assumptions and simplifications will be made
on evaporation interpolation. For instance, in Area H, we only have annual potential evaporation data.
First, we will divide this value by 365 to get the average daily evaporation. Then, interpolate by daily dynamics as assumed.

b. Static input
^^^^^^^^^^^^^^^
Land use at or above surface level are divided into 5 components, namely Paved roofs
(buildings), Closed paved (roads, etc), Open paved (pavements, parkings, etc), Unpaved
(grass land, etc) and Open water (ditches, canals, ponds, etc).
Land use fractions
The fractions of above five land use types should sum up to 100%. And we need total
area of the study area in [m2]
Besides, for paved areas (PR, CP, OP), we also can define three additional types of
fractions:

1. disconnect fraction of three paved areas:
“Part disconnected from sewer”: This disconnect fraction means how
much percentage of the paved area (say paved roofs) is disconnected from the sewer
system. If this fraction is 5%, then it means 5% of the paved roofs (PR) is disconnected
to sewer system. Consequently, 5% of the runoff from the paved roofs (PR) will not end
in the sewer system but will presumably flow to unpaved area.

2. part of building above groundwater (GW):
“part of buildings above GW”: This fraction means, in terms of paved roofs only, how much percentage of paved roofs (PR)
has its bottom of foundation above the phreatic table. As we know, the relationship between the bottom level of
building foundation and variation of groundwater level is essential to building stability,but this safety concern is not
the model concern. What this fraction really matters in the model is the total area size of the (shallow) groundwater (GW).

3. part of open water above groundwater (GW):
“Part of OW above GW”: This fraction is more or less similar to part of building above groundwater (GW). It affects the
calculation of size of groundwater area. Say we have 300m2 open water. If this fraction is zero, then groundwater will not
contain any m2 of this 300m2. If this fraction is 100%, then groundwater will contain this extra 300m2 as all open water
is above the groundwater. To sum up, type 2 and type 3 fractions influence the total area of (shallow) groundwater
(GW). Area is important since all the storage and fluxes in the model are calculated in
depth [mm], so the conversion from one component to another component is dependent
on the area ratio of two components. That is the reason why two additional fractions (type
2 and type 3) are defined to decide the groundwater area more precisely.

Runoff from paved surface to sewer system only occurs when surface interception storage
capacity can no longer handle excessive rainfall.
“Storm Water Drainage System”: Part of urban area with storm water drainage
system.
“Mixed Sewer System”: Part of urban area with mixed sewer system (i.e. combined sewer system).
These two fractions should sum up to 100%.

Design standard / Design rainfall of sewer system.
This part may be a bit confusing, please don’t get puzzled by the notation used i.
Circle 3.b is discharge capacity of SWDS to open water, discharge capacity of MSS to open
water (wet flow condition), discharge capacity of MSS to waste water treatment plant
(dry flow condition).
These three discharge capacities in circle 3.b are used in the model.
Circle 3.a is design rainfall.
Parameters in Circle 3.a are not directly used in the model. They are actually used to
calculated Circle 3.b parameters if there is no direct information on design discharge
capacity of sewer system.In the Netherlands, say if there is no direct information on discharge capacity of SWDS to
open water (actually there is and it is around 21mm/hr to 30mm/hr), then we can do below
calculations:
“t = 2 rainfall” (in Fig 2): Design rainfall intensity of sewer system.
In the Netherlands, the sewer overflow on the street is designed to occur once every
two years. Hence t = 2 year is chosen as the design rainfall return period. Its corresponding
rainfall intensity is 58.7 mm/hr by rainfall statistics. Consequently, for SWDS, the
predefined discharge capacity of the SWDS is then calculated as 58.7(rainfall intensity of
t=2) - 1.6 (interception on paved area) – 2 (storage in SWDS) = 55.1 mm/hr. This
55.1mm/hr is the discharge capacity of SWDS to open water above which sewer water will
overflow onto the street. Similar to SWDS, discharge capacity of MSS to open water is
calculated as 48.1mm/hr above which sewer overflow from MSS onto street will occur.
“t = 1/6 rainfall” (in Fig 2): Design rainfall intensity of combined sewer overflow.
In the Netherlands, the combined sewer overflow onto the open water is designed to occur
six to seven times a year. Hence t= 1/6 is chosen as the design rainfall return period of
combined sewer overflow. Its corresponding rainfall intensity is 27.9 mm/hr by statistics.
Consequently, for MSS, the predefined discharge capacity of the MSS to waste water
treatment plant (WWTP) is in fact the sewer discharge capacity above which sewer
overflow to open water (CSO) will occur, and this discharge capacity is calculated as 27.9 –
1.6 = 26.3mm/hr.









