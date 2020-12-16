class Comportement :
    DONNEUR = 1
    VENDEUR = 2
    NEUTRE = 3


class Home:

    """
        Classe Home simule les foyers qui produisent et qui consomment de l'énergie

        TODO : générer aléatoirement les taux de prod / conso / …
        TODO : implémenter une message queue pour communiquer avec le Market
        TODO : implémenter une shared memory pour mettre à jour la consommation par rapport à la météo
        TODO : implémenter buy, sell, give
    """
    def __init__(self, position):
        """Constructeur de notre classe Home"""
        self.position = position
        self.taux_consommation = 0
        self.taux_production = 0
        self.stockage_max = 0
        self.stockage = 10
        self.argent = 0
        self.comportement = Comportement()

    def buy(self):
        pass

    def sell(self):
        pass

    def give(self):
        pass

    def actionMeteo(self):
        temp = 20
        if temp <= 0 : self.taux_consommation*=1.5
        if temp > 0  and temp <= 12: self.taux_consommation*=1.3
        if temp > 12  and temp <= 18: self.taux_consommation*=1.15
        if temp > 18  and temp <= 22: self.taux_consommation*=1
        if temp > 22  and temp <= 24: self.taux_consommation*=0.75
        if temp > 24  and temp <= 30: self.taux_consommation*=0.9
        if temp > 30  and temp <= 34: self.taux_consommation*=1
        if temp > 34  : self.taux_consommation*=1.2


