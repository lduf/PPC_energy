class Comportement :
    DONNEUR = 1
    VENDEUR = 2
    NEUTRE = 3


class Home:

    def __init__(self, position):
        """Constructeur de notre classe"""
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