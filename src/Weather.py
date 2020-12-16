import math
import random

class Weather:

    """
        La classe définit la température au cours de notre simulation
        Elle tire aléatoirement 5 nombres qui sont stockés pour chaque foyer
        Pour calculer la température du jour, il suffit l'appliquer les coefficients à la fonction de température

        TODO : implémenter une shared memory avec les foyers
        TODO : réfléchir comment prévenir d'un changement de température
    """
    def __init__(self, nb_foyers):
        """Constructeur de notre classe"""
        self.nb_foyers = nb_foyers
        self.date = 0  # int between 0 and 365 -> to get from Market
        self.conditions = [self.weather_conditions() for _ in range(self.nb_foyers)]
        self.temperatures = []
        self.current_temperature() # donne les températures actuelles pour les foyers


    def weather_conditions(self):
        a = random.randint(10, 20)
        b = random.randint(1, 6)
        c = random.randint(2, 5)
        d = random.randint(4, 10)
        p = random.randint(7, 10) / 10
        pass

    def temp(self, position):
        (a,b,c,d,p) = self.conditions[position]
        return a*math.cos(p*(math.pi)+8/365*self.date)+b*math.cos(self.date/30)-c*math.cos(self.date/50)+d

    def curent_temperature(self):
        self.temperatures = [self.temp(x) for x in range(self.nb_foyers)]

    def update_date(self):
        self.date = (self.date+1)%365 # ou self.date = date (qui serait donnnée en argument de la méthode)
        self.curent_temperature()

if __name__ == "__main__":
    print('Météo')