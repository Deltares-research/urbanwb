import numpy as np
import pandas as pd
from .pavedroof import PavedRoof
from .closedpaved import ClosedPaved
from .openpaved import OpenPaved
from .unpaved import Unpaved
from .groundwater import Groundwater
from .unsaturatedzone import UnsaturatedZone
from .sewersystem import SewerSystem
from .openwater import OpenWater
from .selector import soil_selector, et_selector
import time
from pathlib import Path

start = time.time()
# Load csv file

indir = Path('input')
outdir = Path('pysol')
outdir.mkdir(parents=True, exist_ok=True)

InputData = pd.read_csv(indir / 'input_csv.csv')  # input the precipitation, potential evaporation

date = InputData['date']
P_atm = InputData['P_atm']
Ref_grass = InputData['Ref.grass']
E_pot_OW = InputData['E_pot_OW']
iters = np.shape(date)[0]

filename = 'test.csv'  # name the output file

# Parameter settings.
delta_t = 1/24
pr_no_meas_area = 1560
pr_meas_area = 0
pr_meas_inflow_area = 0
cp_no_meas_area = 803.39064064
cp_meas_area = 0
cp_meas_inflow_area = 0
op_no_meas_area = 481.60935936000004
op_meas_area = 0
op_meas_inflow_area = 0
up_no_meas_area = 6855
up_meas_area = 0
up_meas_inflow_area = 0
ow_no_meas_area = 300
uz_no_meas_area = 6855
uz_meas_area = 0
gw_no_meas_area = 8140
gw_meas_area = 0
tot_meas_area = 0
swds_no_meas_area = 2845
mss_no_meas_area = 0
ow_level = 1.5
total_meas_area = 0  # = tot_meas_area
total_area = 10000
# measure inflow:
meas_uz = np.zeros(iters)
meas_gw = np.zeros(iters)
meas_swds = np.zeros(iters)
meas_mss = np.zeros(iters)
meas_ow = np.zeros(iters)
# Run:
# PavedRoof:
Int_pr = [0]
E_atm_pr = [0]
init_intstor_pr_t0 = 0  # Set initial interception storage as 0.
Intstor_pr = [init_intstor_pr_t0]
R_pr_meas = [0]
R_pr_swds = [0]
R_pr_mss = [0]
R_pr_up = [0]

# ClosedPaved:
Intcp_cp = [0]
E_atm_cp = [0]
init_intstor_cp_t0 = 0  # Set initial interception storage as 0.
Intstor_cp = [init_intstor_cp_t0]
R_cp_meas = [0]
R_cp_swds = [0]
R_cp_mss = [0]
R_cp_up = [0]

# OpenPaved:
Intcp_op = [0]
E_atm_op = [0]
init_intstor_op_t0 = 0
Intstor_op = [init_intstor_op_t0]
P_op_gw = [0]
R_op_meas = [0]
R_op_swds = [0]
R_op_mss = [0]
R_op_up = [0]

# Unpaved:
Sum_r_up = [0]
Init_stor_up = [0]
Act_infilcap_up = [0]
Tfac_up = [0]
E_atm_up = [0]
I_up_uz = [0]
fin_stor_up_t0 = 0  # Set initial final storage on the surface of the unpaved area as 0.
Fin_stor_up = [fin_stor_up_t0]
R_up_meas = [0]
R_up_ow = [0]

# Unsaturated zone:
Sum_i_uz = [0]
R_meas_uz = [0]
Theta_h3_uz = [0]
T_alpha_uz = [0]
T_atm_uz = [0]
Gwl_up_uz = [0]
Gwl_low_uz = [0]
Theta_eq_uz = [0]
Capris_max_uz = [0]
P_uz_gw = [0]
init_GWL = 1.5
theta_uz_t0 = soil_selector(2, 1, init_GWL)['moist_cont_eq_rz[mm]'].values  # 1.5m is initial gwl.
Theta_uz = [theta_uz_t0]

# Groundwater:
Sum_p_gw = [0]
R_meas_gw = [0]
Gwl_up = [0]
Gwl_low = [0]
Sc_gw = [soil_selector(2, 1, 1.5)['stor_coef'].values]
H_gw = [0]
S_gw_out = [0]
D_gw_ow = [0]
init_gwl_t0 = 1.5
Gwl = [init_gwl_t0]
Gwl_sl = [0]

# Sewer System:
Sum_r_swds =[0]
R_meas_swds = [0]
Sum_r_mss = [0]
R_meas_mss = [0]
Q_swds_ow = [0]
Q_mss_out = [0]
Q_mss_ow = [0]
prev_so_swds_t0, prev_so_mss_t0, prev_stor_swds_t0, prev_stor_mss_t0 = 0, 0, 0, 0
So_swds = [prev_so_swds_t0]
So_mss = [prev_so_mss_t0]
Stor_swds = [prev_stor_swds_t0]
Stor_mss = [prev_stor_mss_t0]

# Open Water:
Prec_ow = [0]
E_atm_ow = [0]
Sum_r_ow = [0]
Sum_d_ow = [0]
Sum_q_ow = [0]
Sum_so_ow = [0]
R_meas_ow = [0]
Q_ow_out = [0]
init_owl_t0 = 1.5
Owl = [init_owl_t0]

# create instances for each land use component.
m_pr = PavedRoof(init_intstor_pr_t0, pr_no_meas_area, pr_meas_area, pr_meas_inflow_area, intstorcap_pr=1.6,
                 stormfrac_pr=1.0, discfrac_pr=0.0)
m_cp = ClosedPaved(init_intstor_cp_t0, cp_no_meas_area, cp_meas_area, cp_meas_inflow_area, intstorcap_cp=1.6,
                   stormfrac_cp=1.0, discfrac_cp=0.0)
m_op = OpenPaved(init_intstor_op_t0, op_no_meas_area, op_meas_area, op_meas_inflow_area,
                 intstorcap_op=1.6, stormfrac_op=1.0, discfrac_op=0.0, infilcap_op=1.0)

m_up = Unpaved(fin_stor_up_t0, up_no_meas_area, up_meas_area, up_meas_inflow_area, infilcap_up=48, mois_uz_max=249.2,
               k_sat_uz=67.9, intstorcap_up=20)
m_uz = UnsaturatedZone(theta_uz_t0, uz_no_meas_area, uz_meas_area, soiltype=2, croptype=1)

m_gw = Groundwater(init_gwl_t0, gw_no_meas_area, gw_meas_area, seep_def=0, w=100, vc=20000, h_deepgw=21.5,
                   flux=1, soiltype=2, croptype=1)

m_ss = SewerSystem(swds_no_meas_area, mss_no_meas_area, prev_stor_swds_t0, prev_so_swds_t0, prev_stor_mss_t0,
                   prev_so_mss_t0,
                   q_swds_ow_cap=55.1, q_mss_out_cap=26.3, q_mss_ow_cap=48.1, stor_swds_cap=2, stor_mss_cap=9)

m_ow = OpenWater(init_owl_t0, ow_no_meas_area, ow_level, q_ow_out_cap=200)


t = 1

while t <= iters - 1:
    # paved roof
    sol_pr = m_pr.sol(P_atm[t], E_pot_OW[t])
    Int_pr.append(sol_pr[0])
    E_atm_pr.append(sol_pr[1])
    Intstor_pr.append(sol_pr[2])
    R_pr_meas.append(sol_pr[3])
    R_pr_swds.append(sol_pr[4])
    R_pr_mss.append(sol_pr[5])
    R_pr_up.append(sol_pr[6])

    # closed paved
    sol_cp = m_cp.sol(P_atm[t], E_pot_OW[t])
    Intcp_cp.append(sol_cp[0])
    E_atm_cp.append(sol_cp[1])
    Intstor_cp.append(sol_cp[2])
    R_cp_meas.append(sol_cp[3])
    R_cp_swds.append(sol_cp[4])
    R_cp_mss.append(sol_cp[5])
    R_cp_up.append(sol_cp[6])

    # open paved
    sol_op = m_op.sol(P_atm[t], E_pot_OW[t], delta_t)
    Intcp_op.append(sol_op[0])
    E_atm_op.append(sol_op[1])
    Intstor_op.append(sol_op[2])
    P_op_gw.append(sol_op[3])
    R_op_meas.append(sol_op[4])
    R_op_swds.append(sol_op[5])
    R_op_mss.append(sol_op[6])
    R_op_up.append(sol_op[7])

    # unpaved
    sol_up = m_up.sol(P_atm[t], E_pot_OW[t], sol_pr[6], sol_cp[6], sol_op[7], Theta_uz[t - 1], pr_no_meas_area,
                      cp_no_meas_area, op_no_meas_area, ow_no_meas_area, delta_t)
    Sum_r_up.append(sol_up[0])
    Init_stor_up.append(sol_up[1])
    Act_infilcap_up.append(sol_up[2])
    Tfac_up.append(sol_up[3])
    E_atm_up.append(sol_up[4])
    I_up_uz.append(sol_up[5])
    Fin_stor_up.append(sol_up[6])
    R_up_meas.append(sol_up[7])
    R_up_ow.append(sol_up[8])

    # unsaturated zone
    sol_uz = m_uz.sol(sol_up[5], meas_uz[t], tot_meas_area, Ref_grass[t], Gwl[t - 1], delta_t)
    Sum_i_uz.append(sol_uz[0])
    R_meas_uz.append(sol_uz[1])
    Theta_h3_uz.append(sol_uz[2])
    T_alpha_uz.append(sol_uz[3])
    T_atm_uz.append(sol_uz[4])
    Gwl_up_uz.append(sol_uz[5])
    Gwl_low_uz.append(sol_uz[6])
    Theta_eq_uz.append(sol_uz[7])
    Capris_max_uz.append(sol_uz[8])
    P_uz_gw.append(sol_uz[9])
    Theta_uz.append(sol_uz[10])

    # groundwater
    sol_gw = m_gw.sol(sol_uz[9], uz_no_meas_area, sol_op[3], op_no_meas_area, tot_meas_area, meas_gw[t],
                      Owl[t-1], delta_t)
    Sum_p_gw.append(sol_gw[0])
    R_meas_gw.append(sol_gw[1])
    Gwl_up.append(sol_gw[2])
    Gwl_low.append(sol_gw[3])
    Sc_gw.append(sol_gw[4])
    H_gw.append(sol_gw[5])
    S_gw_out.append(sol_gw[6])
    D_gw_ow.append(sol_gw[7])
    Gwl.append(sol_gw[8])
    Gwl_sl.append(sol_gw[9])

    # sewer system
    sol_ss = m_ss.sol(pr_no_meas_area, cp_no_meas_area, op_no_meas_area, sol_pr[4], sol_cp[4], sol_op[5], sol_pr[5],
                      sol_cp[5], sol_op[6], meas_swds[t], meas_mss[t], ow_no_meas_area, tot_meas_area)
    Sum_r_swds.append(sol_ss[0])
    R_meas_swds.append(sol_ss[1])
    Sum_r_mss.append(sol_ss[2])
    R_meas_mss.append(sol_ss[3])
    Q_swds_ow.append(sol_ss[4])
    Q_mss_out.append(sol_ss[5])
    Q_mss_ow.append(sol_ss[6])
    So_swds.append(sol_ss[7])
    So_mss.append(sol_ss[8])
    Stor_swds.append(sol_ss[9])
    Stor_mss.append(sol_ss[10])

    # open water
    sol_ow = m_ow.sol(P_atm[t], E_pot_OW[t], sol_up[8], sol_gw[7], sol_ss[4], sol_ss[6], sol_ss[7], sol_ss[8],
                      meas_ow[t], up_no_meas_area, gw_no_meas_area, swds_no_meas_area, mss_no_meas_area,
                      total_meas_area, total_area, delta_t)
    Prec_ow.append(sol_ow[0])
    E_atm_ow.append(sol_ow[1])
    Sum_r_ow.append(sol_ow[2])
    Sum_d_ow.append(sol_ow[3])
    Sum_q_ow.append(sol_ow[4])
    Sum_so_ow.append(sol_ow[5])
    R_meas_ow.append(sol_ow[6])
    Q_ow_out.append(sol_ow[7])
    Owl.append(sol_ow[8])

    if t % 200 == 0:
        print(f'timestep {t} / {iters}')
    t += 1

np.savetxt(outdir / filename, np.c_[Int_pr, E_atm_pr, Intstor_pr, R_pr_meas, R_pr_swds, R_pr_mss, R_pr_up, Intcp_cp,
                                    E_atm_cp, Intstor_cp, R_cp_meas, R_cp_swds, R_cp_mss, R_cp_up, Intcp_op, E_atm_op,
                                    Intstor_op, P_op_gw, R_op_meas, R_op_swds, R_op_mss, R_op_up, Sum_r_up,
                                    Init_stor_up, Act_infilcap_up, Tfac_up, E_atm_up, I_up_uz, Fin_stor_up, R_up_meas,
                                    R_up_ow, Sum_i_uz, R_meas_uz, Theta_h3_uz, T_alpha_uz, T_atm_uz, Gwl_up_uz,
                                    Gwl_low_uz, Theta_eq_uz, Capris_max_uz, P_uz_gw, Theta_uz, Sum_p_gw, R_meas_gw,
                                    Sc_gw, H_gw, S_gw_out, D_gw_ow, Gwl, Gwl_sl, Sum_r_swds,
                                    R_meas_swds, Sum_r_mss, R_meas_mss, Q_swds_ow, Q_mss_out, Q_mss_ow,
                                    So_swds, So_mss, Stor_swds, Stor_mss, Prec_ow, E_atm_ow, Sum_r_ow, Sum_d_ow,
                                    Sum_q_ow, Sum_so_ow, R_meas_ow, Q_ow_out, Owl],
           fmt="%.8f",
           delimiter=',', header='Int_pr, E_atm_pr, Intstor_pr, R_pr_meas, R_pr_swds, R_pr_mss, R_pr_up, Intcp_cp, '
                                 'E_atm_cp, Intstor_cp, R_cp_meas, R_cp_swds, R_cp_mss, R_cp_up, Intcp_op, E_atm_op, '
                                 'Intstor_op, P_op_gw, R_op_meas, R_op_swds, R_op_mss, R_op_up, Sum_r_up, '
                                 'Init_stor_up, Act_infilcap_up, Tfac_up, E_atm_up, I_up_uz, Fin_stor_up, R_up_meas, '
                                 'R_up_ow, Sum_i_uz, R_meas_uz, Theta_h3_uz, T_alpha_uz, T_atm_uz, Gwl_up_uz, '
                                 'Gwl_low_uz, Theta_eq_uz, Capris_max_uz, P_uz_gw, Theta_uz, Sum_p_gw, R_meas_gw, '
                                 'Sc_gw, H_gw, S_gw_out, D_gw_ow, Gwl, Gwl_sl, Sum_r_swds, '
                                 'R_meas_swds, Sum_r_mss, R_meas_mss, Q_swds_ow, Q_mss_out, Q_mss_ow, '
                                 'So_swds, So_mss, Stor_swds, Stor_mss, Prec_ow, E_atm_ow, Sum_r_ow, Sum_d_ow, '
                                 'Sum_q_ow, Sum_so_ow, R_meas_ow, Q_ow_out, Owl')
df = pd.read_csv(outdir / filename)
df.insert(0, 'Date', date)
df.to_csv(outdir / filename)

end = time.time()
print(f'Model runtime: {end - start:.1f}s')

print("The results have been validated. Exactly the same as excel solutions.")


