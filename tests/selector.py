import pandas as pd
from decimal import Decimal, ROUND_FLOOR


path = 'C:/Users/ZWX/PycharmProjects/UWM/Unit_test/Groundwater/'
soilmatrix = pd.read_csv(path + 'soilparameter_new.csv')
etmatrix = pd.read_csv(path + 'ETparameter.csv')


# ET selector
def et_selector(a, b):
    """defines moisture content - related parameters based on given soil type and crop type."""
    # a --- soil type
    # b --- crop type
    sol = etmatrix.loc[(etmatrix.soil_type == int(a)) & (etmatrix.crop_type == int(b))]
    return sol


def soil_selector(a, b, c):
    """defines parameters of equilibrium moisture content, maximum capillary rise,
    storage coefficient and permeability based on soil type, crop type and initial groundwater level"""
    # a --- soil type
    # b --- crop type
    # c --- initial GWL [m -MSL]
    if 0.0 <= c <= 2.5:
        c = float(Decimal(str(c)).quantize(Decimal('.1'), rounding=ROUND_FLOOR))  # need optimization.
    elif c < 3.0:
        c = 2.5
    elif c < 5.0:
        c = int(c)
    elif c < 10:
        c = 5.0
    else:
        c = 10.0
    rootzone_thickness = 100 * et_selector(a, b)['th_rz_m'].values
    sol = soilmatrix.loc[(soilmatrix.soil_type == int(a)) &
                         (soilmatrix.th_rz == int(rootzone_thickness)) &
                         (soilmatrix.gwl == c)]
    return sol
