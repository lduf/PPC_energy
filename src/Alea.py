import random
import os, signal
import time

class Alea(object) :
    """Cette classe définit les événements  de la simulation
    """

    def __init__(self, risque, event):
        # Définition des éléments statistiques qui peuvent arriver
        self.risque = 1 #risque if (risque > 1 and risque < 3) else 2
        self.event = event
        self.current_risque = 0
        self.current_alea = ("RAS", 0)
        self.date = 0
        self.ppid = os.getppid()
        #print("Ici mon ppid ",self.ppid)
        self.setup()

    def genAlea(self, signum, frame):
            print("QQCH DANS ALEAO Date du jour {}".format(self.date))
            prob = random.randint(0, 10**self.risque)
            print("proba risque :",prob)
            if prob in self.event:
                self.current_alea = self.event[prob]
                print("alea choisi:",self.current_alea)
                os.kill(self.ppid, self.current_alea[2])
            else:
                self.current_alea = ("Ras", 0, 0)
            self.current_risque = self.current_alea[1]
            print("risque:",self.current_risque)
            self.date +=1

    def setup(self):
        print("47 terr j'écouteeeeeee x1")
        signal.signal(signal.SIGUSR1, self.genAlea)  # il choppe le sigusr1 et lance genAlea
        #time.sleep(6)
        while True:
            pass
