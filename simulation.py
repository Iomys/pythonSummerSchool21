"""
Simulation heure par heure prenant en compte la production et la consommation d'énergie

"""
from lib import *
from settings.config import config
cop_froid = 64  # cf. calcul Emmanuel
isolant = Materiau(nom="Un isolant", valeurLambda=0.030)
beton = Materiau(nom="Béton", valeurLambda=2.4)  # écobati.com

mur = Mur((isolant, 30), (beton, 20))
battery = StockageElectrique(config["stockage_electrique"])
hydropack = StockageHydrogene(config["stockage_hydrogene"], config["stockage_hydrogene_depart"])
stock = StockageEau(config["stockage_eau"]["hauteur"], config["stockage_eau"]["largeur"], config["stockage_eau"]["longueur"], mur, temp_depart=config["stockage_eau"]["temp_depart"])
tempChauff = 70
tempECS = 70
pac = PAC(cop=5, puissance=0)
pacNappe = PAC(cop=4, puissance=0)
tempNappe = 10
pertes_tuyaux = 8.28

def sim(heure, prodPV, prodHydro, prodSolTh, consoChal, consoFroid, consoECS, consoElec):
    """
    La fonction *sim* est lancée heure par heure pour une année entière.
    Elle prend en compte l'énergie produite, et les demandes en électricité et chauffage/refroidissement.
    Tout est fait avec des énergies en kWh et non des puissance.

    :param heure: Heure de la simulation (1 à 8760)
    :param prodPV: Production en kWh de solaire photovoltaïque durant l'heure de simulation
    :param prodHydro: Production en kWh d'électricité hydraulique durant l'heure de simulation
    :param prodSolTh: Production en kWh de solaire thermique
    :param consoElec: Consommation en kWh d'électricité (éclairage, appareils...)
    :param consoChal: Consommation en chaleur
    :param consoFroid: Consommation en froid
    :param consoECS: Consommation en eau chaude sanitaire
    :return: bilanElec, consoElec, stock.temp
    """
    log.hour = heure # Utile pour le logging des infos
    prodSolTh_gache = 0


    bilanElec = 0  # Le bilan est positif s'il y a une exportation d'électricité ou négatif en cas d'importation
    prodElec = prodPV + prodHydro

    # Consommation énergétique du quartier
    prodElec -= consoElec

    # Pertes dans les conduites du CAD
    consoChal += pertes_tuyaux

    # Pertes horaires du stockage

    consoChal += stock.pertes_horaires()

    # Chauffage du stock avec les PV
    try:
        stock.entree(prodSolTh*0.8)
    except TemperatureTooHighError:
        prodSolTh_gache = prodSolTh

    # Chauffage du bâtiment avec la PAC qui puisse dans le stock d'anérgie
    if stock.temp >= tempChauff:    # Si le stock est plus chaud que le température, pas besoin de la PAC
        stock.sortie(consoChal)     #
    else:                           # Stock pas assez chaud -> utilisation de la PAC
        enPAC = pac.pomper(demandeEnergie=consoChal, tempChaud=tempChauff, tempFroid=stock.temp)
        try:
            stock.sortie(enPAC["froid"])
        except TemperatureTooLowError:
            print("Température trop faible pour chauffer le chauffage")
        finally:
            prodElec -= enPAC["elec"]
    copChauff = pac.cop
    # Refroidissement avec la nappe phréatique
    prodElec -= consoFroid / cop_froid  # Seulement l'énergie de la pompe de circulation

    # Chauffage de l'ECS avec la PAC qui puise dans le stock d'anergie

    if stock.temp >= tempECS:    # Si le stock est plus chaud que le température, pas besoin de la PAC
        stock.sortie(consoECS)
    else:                        # Stock pas assez chaud -> utilisation de la PAC
        enPAC = pac.pomper(demandeEnergie=consoECS, tempChaud=tempECS, tempFroid=stock.temp)
        try:
            stock.sortie(enPAC["froid"])
        except TemperatureTooLowError:
            print("Température du stock trop faible pour chauffer l'ECS")
        else:
            prodElec -= enPAC["elec"]

    copECS = pac.cop

    if prodElec > 0:  # On stocke de l'électricité excédente dans les batteries
        prodElec -= battery.entree(prodElec)
    else:
        prodElec += battery.sortie(-prodElec)

    # Stockage Hydrogène
    if prodElec > 0:  # On stocke de l'électricité excédente dans les batteries
        prodElec -= hydropack.entree(prodElec)
    else:
        prodElec += hydropack.sortie(-prodElec)



    # Chauffage du stock depuis la nappe phréatique avec l'électricité restante
    if prodElec > 0 and stock.temp < 80 and False:
        elecPac = min(prodElec, config["puissance_pac"])
        prodElec -= elecPac
        enPAC = pacNappe.pomperEnRestante(elecPac, tempChaud=stock.temp+20, tempFroid=tempNappe)
        try:
         stock.entree(enPAC["chaud"])
         bilanElec = 0
        except TemperatureTooHighError:  # Si le stockage est trop chaud, exportation de l'électricité sur le réseau
         bilanElec = prodElec
    else:
        bilanElec = prodElec


    return [heure, bilanElec, stock.energie, stock.temp, copChauff, copECS, prodSolTh_gache, battery.stock_actuel, hydropack.stock_actuel]




