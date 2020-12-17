import random
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
        self.taux_consommation = random.randint(80,700)
        self.current_consommation = self.taux_consommation
        self.taux_production = random.randint(200,1000)
        self.stockage_max = 10000
        self.stockage = 100
        self.argent = 0
        self.comportement = Comportement()
        self.date = 0
        self.temperature = 0

    def buy(self):
        pass

    def sell(self):
        pass

    def give(self):
        pass

    def actionMeteo(self):
        self.current_consommation = self.taux_consommation
        if self.temperature <= 0 : self.current_consommation*=1.5
        if self.temperature > 0  and self.temperature <= 12: self.current_consommation*=1.3
        if self.temperature > 12  and self.temperature <= 18: self.current_consommation*=1.15
        if self.temperature > 18  and self.temperature <= 22: self.current_consommation*=1
        if self.temperature > 22  and self.temperature <= 24: self.current_consommation*=0.75
        if self.temperature > 24  and self.temperature <= 30: self.current_consommation*=0.9
        if self.temperature > 30  and self.temperature <= 34: self.current_consommation*=1
        if self.temperature > 34  : self.current_consommation*=1.2

    def update(self):
        self.date+=1
        self.actionMeteo()
        energie = self.taux_production - self.taux_consommation
        if energie > 0 :
            self.stockage =  self.stockage+energie if self.stockage+energie < self.stockage_max else self.stockage_max
        else :
            self.stockage = self.stockage + energie




