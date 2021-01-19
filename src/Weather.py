import sys
import signal
import math
import random
import sysv_ipc


class Weather:

    """
        La classe définit la température au cours de notre simulation
        Elle tire aléatoirement 5 nombres qui sont stockés pour chaque foyer
        Pour calculer la température du jour, il suffit l'appliquer les coefficients à la fonction de température

    """
    def __init__(self, nb_foyers=4):
        """Constructeur de notre classe"""

        print("FIRST THING IN METEO")
        self.nb_foyers = nb_foyers
        self.date = 0  # int between 0 and 365 -> to get from Market
        self.conditions = [self.weather_conditions() for _ in range(self.nb_foyers)]  # contient les facteurs pour le calcul de la tempé
        self.temperatures = []
        try:
            self.sm = sysv_ipc.SharedMemory(10) # on se connecte à la shared memory
        except sysv_ipc.ExistentialError:
            print("Méteo Cannot connect to shared Memory", 10, ", terminating NOW.")
            sys.exit(1)
        try:
            self.smSema = sysv_ipc.Semaphore(10)
        except sysv_ipc.ExistentialError:
            print("Méteo Cannot connect to semaphore", 10, ", terminating NOW.")
            sys.exit(1)

        self.current_temperature()  # donne les températures actuelles pour les foyers
        self.setup()

        #sm.start()
        #shared_temperature = sm.ShareableList(self.temperatures, name='current_temperature')


    def weather_conditions(self):
        a = random.randint(10, 20)
        b = random.randint(1, 6)
        c = random.randint(2, 5)
        d = random.randint(4, 10)
        p = random.randint(7, 10) / 10
        return (a,b,c,d,p)

    def temp(self, position):
        (a,b,c,d,p) = self.conditions[position]
        return a*math.cos(p*(math.pi)+8/365*self.date)+b*math.cos(self.date/30)-c*math.cos(self.date/50)+d

    def current_temperature(self):
        print("******** Initialisation des températures")
        self.temperatures = [round(self.temp(x),1) for x in range(self.nb_foyers)]
        self.smSema.acquire()
        self.sm.write(str((self.date,self.temperatures)).encode())
        print("Ajout de la météo dans la message queue : -- {} \n --".format(str(self.temperatures).encode()))
        self.smSema.release()


    def update_date(self, signum, frame):
        self.date +=1# ou self.date = date (qui serait donnnée en argument de la méthode)
        self.current_temperature()
                #print(self.temperatures)

    def setup(self):
        signal.signal(signal.SIGUSR1, self.update_date)
        print("Météo is on")
        while True:
            pass


if __name__ == "__main__":
    print('Météo')
