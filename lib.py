class TemperatureTooLowError(Exception):
    pass


class TemperatureTooHighError(Exception):
    pass

class Logger:
    sim_number = 0
    hour = 0
    file_path = ""

    def print(self, title ,message) :
        with open(self.file_path, 'a') as file :
            file.write(f"{self.sim_number} | {self.hour} | {title} : {message}")

log = Logger()
class Batiment:
    """
    Classe de bâtiment basique (pavé)
        1 seul type d'affectation : habitat collectif
        A configurer : largeur, hauteur, longueur, étages
        Facultatif : nombre d'habitants et d'appartements
    """
    def __init__(self, largeur, hauteur, longueur, etages, habitants=None, appartements=None, sousSol=True):
        self.largeur = largeur
        self.hauteur = hauteur
        self.longueur = longueur
        self.etages = etages
        self.habitants = habitants
        self.appartements = appartements

        self.SRE = largeur * longueur * etages  # TODO faut-il diminuer la surface pour prendre en compte les couloirs
        self.Ath = 2*largeur*hauteur + 2 * longueur * hauteur + longueur*largeur * (1.5 if sousSol else 1.8)
        self.fact_forme = self.Ath/self.SRE
        # Besoins de chauffage limites


class Materiau:
    def __init__(self, nom, valeurLambda=None, capaciteCalorifique=None):
        self.nom = nom
        self.valeurLambda = valeurLambda
        self.capaciteCalorifique = capaciteCalorifique


class Mur:
    """
    :param Rentrer un tuple contenant le matériau et l'épaisseur (en cm)
    Exemple : (laineVerre030, 20)
    """
    materiaux = []
    epaisseurs = []

    def __init__(self, *args: tuple):
        for arg in args:
            self.materiaux.append(arg[0])
            self.epaisseurs.append(arg[1])

            self.epaisseur = sum(self.epaisseurs)
        # Calcul de U (en passant par R)
        Rth = 0
        for i in range(len(self.materiaux)):
            Rth += self.epaisseurs[i]/100 / self.materiaux[i].valeurLambda

        self.valeurU = 1/Rth


class StockageEau:
    def __init__(self, hauteur, longueur, largeur, mur):
        self.mur = mur
        self.largeur = largeur
        self.longueur = longueur
        self.hauteur = hauteur
        self.volume = longueur*hauteur*largeur

        # Calcul de la masse
        self.masseVolumique = 998  # kg/m³
        self.masse = largeur * longueur * hauteur * self.masseVolumique # kg

        # Calcul de la capacité thermique
        self.tempMin = 14
        self.temp = self.tempMin # Température de départ pour la simulation
        self.tempMax = 95
        deltaT = self.tempMax - self.tempMin
        self.capaciteCalorifique = 4180  # Capacité calorifique massique (J/kg·K)
        self.capaciteThermique = self.masse * deltaT * self.capaciteCalorifique / 3.6e6

        # Calcul des échanges de chaleur

    def entree(self, energie):
        if self.temp < self.tempMax:
            # L'énergie injectée est transformée en température.
            energieJoules = energie * 3.6e+6
            deltaT = energieJoules / (self.masse * self.capaciteCalorifique)
            self.temp += deltaT
        else:
            raise TemperatureTooHighError(f"La température {self.temp} est trop élevée (TempMax : {self.tempMax})")

    def sortie(self, energie):
        if self.temp > self.tempMin:
            # L'énergie injectée est transformée en température.
            energieJoules = energie * 3.6e+6
            deltaT = energieJoules / (self.masse * self.capaciteCalorifique)
            self.temp -= deltaT
        else:
            raise TemperatureTooLowError(f"La température {self.temp} est trop faible (TempMin : {self.tempMin})")

    def pertes_horaires(self, tempExt):
        """
        Calcul des pertes horaires en fonction de la température externe
        # TODO : ajouter les pertes horaires du système de stockage.
        :param tempExt:
        :return:
        """
    @property
    def energie(self):
        """
        Calcul l'énergie stockée dans le stock
        :return:
        """
        return (self.temp - self.tempMin) * self.capaciteCalorifique * self.masse / 3.6e6


class PAC:
    def __init__(self, cop, puissance, carnotFactor=2):
        self.puissance = puissance
        self.cop = cop
        self.carnotFactor = carnotFactor  # Chiffre à diviser pour obtenir le rendement de Carnot

    def calculer_rendement(self, tempChaud, tempFroid):
        """

        :param tempChaud: Température de l'eau chaude (en °C)
        :param tempFroid: Température de la source froide
        :return: Coefficient de performance de la PAC
        """
        zero_absolu = 273.15
        tempChaud += zero_absolu # Conversion Degrés en Kelvin
        tempFroid += zero_absolu
        cop = tempChaud/(tempChaud-tempFroid)  # Calculs du rendement de Carnot
        cop /= self.carnotFactor  # Rendement
        self.cop = cop
        return cop

    def pomper(self, demandeEnergie, tempFroid, tempChaud):
        """
        Pompe l'énergie quelque part (ça peut être la nappe ou le stock d'anérgie).
        Pompe seulement une certaine quantité d'énergie thermique demandée.
        :param demandeEnergie:
        :param tempChaud: Température de l'eau chaude (en °C)
        :param tempFroid: Température de la source froide
        :return: Dictionnaire avec l'énergie demandée à la source froide ("froid") et l'énergie électrique nécessaire
        ("elec")
        """
        cop = self.calculer_rendement(tempChaud=tempChaud, tempFroid=tempFroid)
        #  Source : https://fr.wikipedia.org/wiki/Coefficient_de_performance
        demandeFroid = (1-1/cop) * demandeEnergie  # Demande en énergie de la source froide
        demandeElec = 1/cop * demandeEnergie
        return {"froid": demandeFroid, "elec": demandeElec}  # Demande en énergie électrique

    def pomperEnRestante(self, energieElec, tempFroid, tempChaud):
        """
        Permet de pomper en fournissant une certaine quantité d'énergie électrique
        Fonction utilisée principalement pour stocker l'énergie
        :param energieElec: Energie électrique fournie
        :param tempChaud: Température de l'eau chaude (en °C)
        :param tempFroid: Température de la source froide
        :return: Dictionnaire avec la chaleur produire ("chaud") et l'énergie prélevée à la source froide ("froid")
        """
        cop = self.calculer_rendement(tempChaud=tempChaud, tempFroid=tempFroid)
        return {"chaud": energieElec*cop, "froid": energieElec*(cop-1)}
