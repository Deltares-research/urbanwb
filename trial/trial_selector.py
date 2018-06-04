import pandas as pd

path = 'input/'
soilmatrix = pd.read_csv(path + 'soilparameter_new.csv')
etmatrix = pd.read_csv(path + 'etparameter.csv')


# ET selector
def et_selector(a, b):
    """defines moisture content - related parameters based on given soil type and crop type."""
    # a --- soil type
    # b --- crop type
    sol = etmatrix.loc[(etmatrix.soil_type == int(a)) & (etmatrix.crop_type == int(b))]
    return sol


def soil_selector(a, b):
    """returns a database of soil parameters of equilibrium moisture content, maximum capillary rise,
    storage coefficient and permeability based on soil type, crop type"""
    # a --- soil type
    # b --- crop type

    rootzone_thickness = 100 * et_selector(a, b)['th_rz_m'].values
    soil_prm = soilmatrix.loc[(soilmatrix.soil_type == int(a)) &
                              (soilmatrix.th_rz == int(rootzone_thickness))]
    soil_prm = soil_prm.to_dict(orient="Records")

    return soil_prm


if __name__ == '__main__':
    print(soil_selector(2, 1))
    print(soil_selector(5, 1)[29]['capris_max[mm/d]'])
    k_sat_uz = 10 * soil_selector(2, 1)[0]['k_sat']
    mois_uz_max = soil_selector(2, 1)[0]['moist_cont_eq_rz[mm]']
    print(k_sat_uz, mois_uz_max)
