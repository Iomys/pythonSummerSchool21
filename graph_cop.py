from lib import PAC
import matplotlib.pyplot as plt
import numpy as np

pac = PAC(cop=3, puissance=4, carnotFactor=2)

tab_cop = np.zeros((3, 60))
tab_cop[0] = np.linspace(-5, 25, 60)

for i in range(0,60):
    tab_cop[1][i] = pac.calculer_rendement(tempFroid=tab_cop[0][i], tempChaud=35)
    tab_cop[2][i] = pac.calculer_rendement(tempFroid=tab_cop[0][i], tempChaud=55)

plt.plot(tab_cop[0], tab_cop[1], tab_cop[0], tab_cop[2])
plt.legend(["PAC chauffage", "PAC ECS"])
plt.grid()
plt.ylim(0)
plt.ylabel("Coefficient de performance")
plt.xlabel("Température [°C]")
plt.savefig("plots/cop_selon_carnot.svg")
