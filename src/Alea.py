import random
class Alea :
    """Cette classe définit les événements politiques de la simulation"""

    def __init__(self, risque, event):
        # Définition des éléments statistiques qui peuvent arriver
        self.risque = risque if (risque > 4 and risque < 10) else 8
        self.event = event
        self.current_risque = 0
        self.current_alea = ("RAS", 0)


    def genAlea(self):
        prob = random.randomint(0, 10**self.risque)
        if prob in self.event:
            self.current_alea = self.event[prob]
        else:
            self.current_alea = ("Ras", 0)
        self.current_risque = self.current_alea[1]
