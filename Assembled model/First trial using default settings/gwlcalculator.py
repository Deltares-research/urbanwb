from decimal import Decimal, ROUND_FLOOR
import numpy as np

def gwlcal(x):
    """calculates the groundwater up and groundwater low"""
    gwl_up = float(x)
    if 0 <= gwl_up <= 2.5:
        gwl_up = float(Decimal(str(gwl_up)).quantize(Decimal('.1'), rounding=ROUND_FLOOR))
    elif gwl_up < 3.0:
        gwl_up = 2.5
    elif gwl_up < 5.0:
        gwl_up = int(gwl_up)
    elif gwl_up <= 10:
        gwl_up = 5.0
    else:
        gwl_up = 10

    if gwl_up < 2.5:
        gwl_low = round(gwl_up + 0.1, 2)
    elif gwl_up < 3:
        gwl_low = 3
    elif gwl_up < 4:
        gwl_low = 4
    elif gwl_up < 5:
        gwl_low = 5
    else:
        gwl_low = 10
    return gwl_up, gwl_low
