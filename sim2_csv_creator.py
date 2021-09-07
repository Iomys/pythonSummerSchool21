#%%

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#from main import numero_sim

def csv_create():
    numero_sim = 2
    sim_dir = f"data/sims/sim{numero_sim}"

    #%% md

    # Besoins en chaud et en froid

    #%%

    chaud_froid = pd.read_csv(f"{sim_dir}/inputs/puissance_chaud_froid.csv", delimiter=",", skiprows=[1,2])

    chaud_froid = chaud_froid.drop(axis=1, labels=[f"Unnamed: {i}" for i in range(0, 24, 2)])
    chaud_froid.sort_index(axis=1, inplace=True)
    legends = ['A1 bureau', 'A1 habitations', 'A3', 'B2 bureau', 'B2 habitations',
               'C1 dépôt', 'C1 habitations', 'C1 restauration', 'C2 bureau', 'C2 habitations',
               'D1 ferme', 'D2 dépôt']
    SRE = [9450, 1890, 17010, 10800, 2700, 1350, 675, 675, 4050, 1350, 855,900]
    for i in range(0, len(SRE)):
        chaud_froid.iloc[:, i] = chaud_froid.iloc[:, i] * SRE[i]

    #%%

    froid = chaud_froid[chaud_froid.lt(0)].sum(axis=1)
    chaud = chaud_froid[chaud_froid.gt(0)].sum(axis=1)
    maj = chaud_froid.sum(axis=1)
    #chaud.plot()
    #froid.plot()
    #(maj-chaud-froid).plot()
    #chaud_froid.to_csv("chaud_froid.csv")

    #%%

    #(chaud_froid.lt(0) or chaud_froid.gt(0)).sum(axis=1).sum()
    #(chaud+ froid).plot()
    chaud.max()

    #%% md

    # Production solaire PV et thermique

    #%%

    sol_pv = pd.read_csv(f"{sim_dir}/inputs/solaire_pv2.csv", comment="#", delimiter=";")
    sol_pv = sol_pv.iloc[:, 0]

    sol_th = pd.read_csv(f"{sim_dir}/inputs/solaire_thermique.csv", comment="#", delimiter=";")

    surface_toiture = 11850 # m2

    prop_pv = 0.21
    prop_th = 0.05
    sol_th = sol_th.iloc[:8761, 1:4]
    prod_sol_th = sol_th*prop_th*surface_toiture
    prod_sol_pv = sol_pv*prop_pv*surface_toiture
    #prod_sol_th.rolling(window=24*7*4).sum().plot()
    #prod_sol_pv.rolling(window=24*7*4).sum().plot()

    #%% md

    # Eau chaude sanitaire

    #%%

    ecs = pd.read_csv(f"{sim_dir}/inputs/ecs.csv", delimiter=";", index_col=0)
    ecs.sum(axis=1).sum()
    #ecs.iloc[1:24].plot.area(stacked=True)

    #%% md

    # Production Hydraulique

    #%%

    hydro = pd.read_csv(f"{sim_dir}/inputs/hydro.csv", delimiter=";", comment="#")
    #hydro = pd.DataFrame([0 for i in range(0,8761)])
    #%% md

    # Consommation électrique

    #%%

    ele=pd.read_csv(f"{sim_dir}/inputs/ele.csv", delimiter=";", comment="#")

    #%% Final


    final = pd.DataFrame(froid)
    final["heure"] = pd.DataFrame([i for i in range(1,8761)])
    final.set_index(keys="heure", inplace=True)
    final["prodPV"] = prod_sol_pv
    final["prodHydro"] = hydro
    final["prodSolTh"] = prod_sol_th["90"]

    final["consChal"] = chaud / 1000
    final["consECS"] = ecs.sum(axis=1)
    final["consFroid"] = - froid/1000
    final["consElec"] = ele
    final.drop(columns=0, inplace=True)
    final.to_csv(f"{sim_dir}/input_data.csv", na_rep="0")
    final.to_numpy(na_value=0,)

    #%%

    final["consECS"].max(), final["consChal"].max()

