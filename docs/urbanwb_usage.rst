Running the model
*****************
Overview
--------

The script model can be run from windows command prompt or with ``run.bat`` file. The latter choice is highly recommended.

For the time being, the most commonly used function is **savecsv**, **batch-run-sdf** and **batch-run-measure**

The ``running_sample`` folder in the Urbanwb package includes the sample of running the model for both basic model and model with measure.

Two input are necessary to start the Urbanwb model:

``Dynamic input``: The forcing --- Hourly time series of Precipitation, potential open water evaporation and potential reference crop evapotranspiration.
The user is responsible for data preprocessing --- clean data, fill vacancy, remove unrealistic data and make sure the data is in float type.
Make sure the column name is the same because script use the column name to index which data is precipitation and evaporation.

``Static input``: All the static input parameters are stored in the configuration file suffixed with ``.ini``.
Currently, two configuration files are indispensable for every function to use ---  one is neighbourhood configure file,
the other is measure configuration file. If no measure is included in the modelling, please specify ``measure_appled=false``
in measure configuration file. Though the script will automatically do some checks after reading the configuration file to make
it fool proof, for example it will update the measure-related area with zero if no measure is applied even if it is not zero due to user's
carelessness, it is highly recommended that user carefully deal with the configuration input. Besides, user should modify the
parameters according to the local context of his area of interest and expected setups. Be aware of not changing the parameter
name, otherwise the model goes wrong. The descriptions of the parameter are in the configuration file, documentation and script docstings
for user's cross check.

Input time series and parameters
------------------------------------------------

a. Time series (Dynamic input)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The forcing of Urbanwb model is the time series of:

+ precipitation (only rainfall considered)
+ potential open water evaporation (i.e. Penman evaporation [Penman]_.)
+ potential reference crop evapotranspiration (i.e. Penman-Monteith evaporation [Monteith]_ or Makkink evaporation.)

.. note::

    Sometimes, Penman evaporation is not directly available since it is not straightly measured, while (class-A) pan
    evaporation data is more easier to find. Pan evaporation Usually, pan evaporation is multiplied a correlation factor 0.77 to convert
    to Penman evaporation [Linacre]_. The model assumes potential open water evaporation actual interception evaporation on paved surface





Even though
Forcing: Hourly time series of precipitation (actually only rainfall) [mm] and potential evaporation of
open water [mm]. (for grass, it is approximately 0.8982 * Penman evaporation [Droogers]_.)
Length should better be most recent 30 years. Atmosphere is the most crucial exchange to the model.
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

b. Parameters (Static input)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
This fraction indicates
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


Functions
---------
1. save_to_csv
~~~~~~~~~~~~~~~
This function performs single run of the model. It can save all results or selected results in to an output csv file.

.. code-block:: python

   # save all results
   #         module name               func name   timeseries name neighbourhood measure  outputfile
   python -m urbanwb.main_with_measure save_to_csv timeseries.csv config1.ini config2.ini output.csv

   # save selected results
   #         module name               func name   timeseries name neighbourhood measure  outputfile variable to save        save_all is False -> save selected
   python -m urbanwb.main_with_measure save_to_csv timeseries.csv config1.ini config2.ini output.csv owl r_pr_swds  theta_uz --save_all=False


2. batch_run_sdf
~~~~~~~~~~~~~~~~
This function performs batch run on different pumping capacity to produce database which can be used to plot Storage-Discharge-Frequency (SDF) Curve

.. code-block:: python

   # mean daily rainfall as baseline q, batch run [4,5]
   #         module name                  function      ts.csv    config1.ini          config2.ini    output.csv      random number     baseline q default
   python -m urbanwb.main_with_measure batch_run_sdf ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep2_results.csv --q_list=[4,5]

   # 4 as baseline q, batch run [10,20]
   #         module name                  function      ts.csv    config1.ini          config2.ini    output.csv      random number     baseline q predefined
   python -m urbanwb.main_with_measure batch_run_sdf ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep2_results1.csv --q_list=[10,20] --baseline_q=4

   # 3 as baseline q, batch run [min,max,steps] --- [4,8,3]
   #         module name                  function      ts.csv    config1.ini          config2.ini    output.csv      [min,max,steps]   baseline q:predefined AP:True to enable [min,max,steps]. if False, then q_list random numbers
   python -m urbanwb.main_with_measure batch_run_sdf ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep2_results2.csv --q_list=[4,8,3] --baseline_q=3 --arithmetic_progression=True


3. batch_run_meas
~~~~~~~~~~~~~~~~~
This functoin performs batch run on measure. First do batch run with different (pairs of) values, then do baseline run (no measure).
In the end, save the runoff time series into a csv file.

It can vary one parameter with a list of values or vary two parameters at the same time.

.. code-block:: python

   #          module                    function          ts.csv    config1.ini          config2.ini    output.csv      var to change               value to update var   corresp var        value for corresp var  baseline runoff               measure runoff to save
   python -m urbanwb.main_with_measure batch_run_measure ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep3_results.csv --varkey="storcap_btm_meas" --vararrlist1=[1050,1200] --correspvarkey=None --vararrlist2=None --baseline_variable="r_cp_swds" --variable_to_save="q_meas_swds"

   python -m urbanwb.main_with_measure batch_run_measure ep_ts.csv ep_neighbourhood.ini ep_measure.ini ep3_results.csv --varkey="storcap_btm_meas" --vararrlist1=[1050,1200] --correspvarkey="runoffcap_btm_meas" --vararrlist2=[30,40] --baseline_variable="r_cp_swds" --variable_to_save="q_meas_swds"

   python -m urbanwb.getconstants ep3_results.csv --num_year=30


References
----------
.. [Droogers] DROOGERS, P. Verbetering bepaling actuele verdamping voor het strategisch waterbeheer. Deﬁnitiestudie. STOWA, 2009.
.. [Penman] PENMAN, Howard Latimer. Natural evaporation from open water, bare soil and grass. Proc. R. Soc. Lond. A, 1948, 193.1032: 120-145.
.. [Monteith] MONTEITH, John L., et al. Evaporation and environment. In: Symp. Soc. Exp. Biol. 1965. p. 4.
.. [Linacre] LINACRE, Edward T. Estimating US Class A pan evaporation from few climate data. Water International, 1994, 19.1: 5-14.


