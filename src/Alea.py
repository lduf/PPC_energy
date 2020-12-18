import random
import os, signal
from functools import partial

class Alea(object) :
    """Cette classe définit les événements  de la simulation"""

    def __init__(self, risque, event):
        # Définition des éléments statistiques qui peuvent arriver
        signal.signal(signal.SIGUSR1, self.genAlea)
        self.risque = risque if (risque > 4 and risque < 10) else 1
        self.event = event
        self.current_risque = 0
        self.current_alea = ("RAS", 0)
        self.date = 0

        self.setup()

    def genAlea(self, signum, frame):
        prob = random.randint(0, 10**self.risque)
        if prob in self.event:
            self.current_alea = self.event[prob]
        else:
            self.current_alea = ("Ras", 0)
        self.current_risque = self.current_alea[1]
        self.date +=1

    def setup(self):
        while True:
            pass


