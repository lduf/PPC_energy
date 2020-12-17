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

    """
    def __init__(self, nb_foyer=4, speed = 4, risque_politique = 5, risque_economique = 8):

        self.date = Value('i',0) #(date du jour)
        self.nb_foyers = nb_foyer
        self.foyers = [Home.Home(i) for i in range(self.nb_foyers)] #Foyer participant au market
        self.wea = Weather.Weather(self.nb_foyers) # météo =>
        self.pol = Politic.Politic(risque_politique)
        self.econ =  Economic.Economic(risque_economique)
        self.price = 10 # prix de l'énergie au temps t
        self.price_t = 10 #prix au temps -1
        self.speed = speed #prix au temps -1

        self.current_consommation = 0 # à calculer en accédant à toutes les consommations des homes
        self.current_production = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie = 0  # à calculer en accédant à toutes les productions des homes
        self_total_energie_1 = 0
    def calc_production(self):
        self.total_energie_1 = self.total_energie
        self.total_energie = 0
        self.current_production = 0
        self.current_consommation = 0
        for foyer in self.foyers:
            self.current_production += foyer.taux_production
            self.current_consommation += foyer.current_consommation
            self.total_energie+=foyer.stockage

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

        #signaux détournés pour notre usage
        signal.signal(signal.SIGUSR1, self.pol.genAlea)
        signal.signal(signal.SIGUSR2, self.econ.genAlea)
        signal.signal(signal.SIGBUS, self.wea.update_date)

        # lancement des process
        polProcess = Process(target=self.pol.setup, args=())
        econProcess = Process(target=self.econ.setup, args=())
        weatherProcess = Process(target=self.wea.setup, args=())
        aleaProcesss = [polProcess, econProcess, weatherProcess]
        for process in aleaProcesss:
            process.start()

        plt.figure()
        t= [x for x in range(365)]
        prix = []
        energie = []
        while self.date.value < 365 :
            if self.date.value > 364-1:
                for process in aleaProcesss:
                    os.kill(process.pid, signal.SIGKILL)


            # 1. J'aurais préféré utilisé une mémoire partagée pour la date qui marche pour un tick mais bon on doit passer par des signaux
            # 2. je ne sais pas pourquoi mais ça ne marche pas de faire un os.kill(child_id, signal.SIGUSR1) (genre meme en disant qu'on intercepte le signal celui ci n'est pas intercepté)
            self.date.value+=1
            #print("##### ####")
            #print("Date du jour : {}".format(self.date.value))
            os.kill(os.getpid(), signal.SIGUSR1) # on va envoyer nos signaux pour traiter dans les process
            os.kill(os.getpid(), signal.SIGUSR2) # on va envoyer nos signaux pour traiter dans les process
            os.kill(os.getpid(), signal.SIGBUS) # on va envoyer nos signaux pour traiter dans les process
            #print("Politic risque : {}".format(self.pol.current_risque))
            #print("Econ risque : {}".format(self.econ.current_risque))
            #print("Météo ville  : {}".format(self.wea.temperatures))

            for key,foyer in enumerate(self.foyers):
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
        plt.show()
