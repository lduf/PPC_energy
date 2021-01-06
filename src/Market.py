# Market file
import Politic, Economic, Weather, Home
import time, os, signal, math
from multiprocessing import Process, Value, Array
import multiprocessing
import matplotlib.pyplot as plt


class Market :
    """ Classe market qui gère un peu tout le système
        TODO : lancer l'execution en multithread des foyers
        TODO : implémenter la message queue entre Home.py et Market.py
        TODO : implémenter buy et sell
        TODO : refaire calc price
        TODO : refaire calc production

    """
    def __init__(self, nb_foyer=4, speed = 4, risque_politique = 5, risque_economique = 8):

        self.date = Value('i',-1) #(date du jour) Value pour la shared mémory ('i' pour int)
        self.nb_foyers = nb_foyer
        self.foyers = [Home.Home(i) for i in range(self.nb_foyers)] #Foyer participant au market
        self.wea = Weather.Weather(self.nb_foyers) # météo =>
        #self.pol = Politic.Politic(risque_politique)
        self.pol =Process(target=Politic.Politic, args=(risque_politique,))
        self.pol.start()
        self.econ =Process(target=Economic.Economic, args=(risque_economique,))
        self.econ.start()
        #self.econ =  Economic.Economic(risque_economique)
        self.price = 10 # prix de l'énergie au temps t
        self.price_t = 10 #prix au temps t-1
        self.speed = speed #vitesse de la simulation

        self.current_consommation = 0 # à calculer en accédant à toutes les consommations des homes
        self.current_production = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie_1 = 0

    # TODO à refaire
    #fait à la va vite sans trop réfléchir
    def calc_production(self):
        self.total_energie_1 = self.total_energie
        self.total_energie = 0
        self.current_production = 0
        self.current_consommation = 0
        for foyer in self.foyers:
            self.current_production += foyer.taux_production
            self.current_consommation += foyer.current_consommation
            self.total_energie+=foyer.stockage

    #TODO à refaire
    # fait à la va vite sans trop réfléchir
    def calc_price(self):
        etat_reseau = self.current_consommation / self.current_production # facteur qui augmente au diminue le prix en fonction de l'état de la conso/prod
        etat_alea = (self.pol.current_risque + self.econ.current_risque) #somme des composantes polituqes et économiques
        future_price_t = self.price
        energieTotalFactor = math.log(etat_reseau)/abs(math.log(etat_reseau))
        self.price = self.price_t + 1/100*etat_reseau*self.price_t*energieTotalFactor + etat_alea
        self.price_t = future_price_t

    def buy(self):
        pass

    def sell(self):
        pass

    def run(self):

        #plt.figure()
        #t= [x for x in range(365)]
        #prix = []
        #energie = []
        while self.date.value < 365 :
            # 1. J'aurais préféré utilisé une mémoire partagée pour la date qui marche pour un tick mais bon on doit passer par des signaux

            print("##### ####")
            print("Date du jour : {}".format(self.date.value))
            print("{} : {}".format(self.pol.name, self.pol.is_alive()))
            print("{} : {}".format(self.econ.name, self.econ.is_alive()))

            if(self.date.value >= 0):
                os.kill(self.pol.pid, signal.SIGUSR1) # on va envoyer nos signaux pour traiter dans les process
                os.kill(self.econ.pid, signal.SIGUSR1) # on va envoyer nos signaux pour traiter dans les process

            #print("Politic risque : {}".format(self.pol.current_risque))
            #print("Econ risque : {}".format(self.econ.current_risque))
            #print("Météo ville  : {}".format(self.wea.temperatures))

            self.date.value += 1
            time.sleep(2)#self.sleep

        """    for key,foyer in enumerate(self.foyers):
                foyer.temperature = self.wea.temperatures[key]
                foyer.update()

            self.calc_production()
            self.calc_price()
            prix.append(self.price)
            energie.append(self.total_energie)
            #print("Production mondiale : {}\n Consommation mondiale : {}\n Energie totale : {}".format(self.current_production, self.current_consommation, self.total_energie))
            #print("Prix de l'énergie : {}".format(self.price))
            #time.sleep(self.speed)
        plt.subplot(221)
        plt.plot(t,prix)
        plt.title("Prix de l'énergie")
        plt.grid(True)
        plt.subplot(222)
        plt.plot(t, energie)
        plt.title("Quantité de l'énergie")
        plt.grid(True)
        plt.show()"""
