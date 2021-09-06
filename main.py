#%%
from lib import log
from simulation import sim
import numpy as np
import matplotlib.pyplot as plt
#%%

## PARAMS
numero_sim = 0
log.sim_number= numero_sim
path = f"data/sims/sim{numero_sim}"
log.file_path = f"{path}/log.txt"
input_filename = f"{path}/input_data.csv"
data = np.loadtxt(input_filename, delimiter=";", comments="#", skiprows=1)
#print(data)

#%%
# Equivalence des colonnes dans le csv:
COLS_EQ = {
    "heure": 0,
    "prodPV": 1,
    "prodHydro": 2,
    "prodSolTh": 3,
    "consChal": 4,
    "consECS": 5,
    "consFroid": 6,
    "consElec": 7,
}
results = np.empty((len(data), 6))
for line in data:
    #sim_results = sim(heure=1, prodPV=0, prodHydro=0, prodSolTh=100, consoChal=0,
    #              consoFroid=0, consoECS=0, consoElec=0)
    #sim_results = sim(line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7])
    sim_results = sim(heure=line[COLS_EQ["heure"]], prodHydro=line[COLS_EQ["prodHydro"]], prodPV=line[COLS_EQ["prodPV"]], prodSolTh=line[COLS_EQ["prodSolTh"]],
        consoChal=line[COLS_EQ["consChal"]], consoECS=line[COLS_EQ["consECS"]], consoFroid=line[COLS_EQ["consFroid"]],
        consoElec=line[COLS_EQ["consElec"]])
    results[int(line[0])-1] = sim_results

exportfile = open(f"{path}/results.csv", "w")
np.savetxt(exportfile, comments="", fmt="%f", X=results, delimiter=";", newline="\n", header="Heure; Bilan [kWh]; Stockage [kWh]; Température du stock [°C]; COP chauffage; COP ECS")
exportfile.close()
fig, ax1 = plt.subplots()

ax2 = ax1.twinx()

ax2.plot(results[:, 0], results[:, 4])  # cop de la PAC de chauffage

ax2.plot(results[:, 0], results[:, 5])  # cop de la PAC pour l'ECS
ax1.plot(results[:, 0], results[:, 2])  # bilan énergie
ax1.plot(results[:, 0], results[:, 3])  # énergie dans le stock
ax1.set_ylabel("Energie [kWh]")
ax2.set_ylabel("COP des PAC")
ax1.set_xlabel("Heures de l'année")
fig.legend(["PAC chauffage", "PAC ECS", "Bilan énergie", "Energie stockée"])
plt.show()

