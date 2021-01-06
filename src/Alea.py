import random
import os, signal

class Alea(object) :
    """Cette classe définit les événements  de la simulation
        TODO :  communiquer de Alea à Market
    """

    def __init__(self, risque, event):
        # Définition des éléments statistiques qui peuvent arriver
        self.risque = risque if (risque > 4 and risque < 10) else 1
        self.event = event
        self.current_risque = 0
        self.current_alea = ("RAS", 0)
        self.date = 0
        self.setup()

    def genAlea(self, signum, frame):
            #print("Date du jour {}".format(self.date))
            prob = random.randint(0, 10**self.risque)
            if prob in self.event:
                self.current_alea = self.event[prob]
            else:
                self.current_alea = ("Ras", 0)
            self.current_risque = self.current_alea[1]
            self.date +=1

    def setup(self):
        signal.signal(signal.SIGUSR1, self.genAlea)  # il choppe le sigusr1 et lance genAlea
        while True:
            pass


"""
import signal
import time
from multiprocessing import Process

from os import *

c = 0

def child():
    time.sleep(5)
    kill(getppid(), signal.SIGUSR1)
    time.sleep(5)
    print("Not dead yett !!")

def handler(sig, frame):
    if sig == signal.SIGUSR1:
        kill(c, signal.SIGKILL)
        print("Le parent tue l'enfant de pid :", c)


if __name__ == "__main__":

    signal.signal(signal.SIGUSR1, handler)

    print("Parent process PID :", getpid())
    p = Process(target=child, args=())
    p.start()
    c = p.pid
    print("Child process PID :", c)
    p.join()
"""
