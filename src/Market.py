# Market file
import concurrent
import ast
import Politic, Economic, Weather, Home
import time, os, signal, math
import sysv_ipc
from multiprocessing import Process, Value, Array
import threading
import sys
import concurrent.futures
import matplotlib.pyplot as plt


class Market :
    """ Classe market qui gère un peu tout le système
        TODO : lancer l'execution en multithread des foyers
        TODO : implémenter la message queue entre Home.py et Market.py
        TODO : implémenter buy et sell
        TODO : refaire calc price
        TODO : refaire calc production
        TODO : multiprocessing.barrier

    """
    def __init__(self, nb_foyer=4, speed = 4, risque_politique = 5, risque_economique = 8):

        self.data_ready = threading.Event()
        self.date = Value('i',-1) #(date du jour) Value pour la shared mémory ('i' pour int)
        self.nb_foyers = nb_foyer
        self.foyers = [threading.Thread(target=Home.Home, args=(i, self.date, )) for i in range(self.nb_foyers)]  #Foyer participant au market
        try:
            self.mq = sysv_ipc.MessageQueue(12, sysv_ipc.IPC_CREX)
        except sysv_ipc.ExistentialError:
            print("Message queue", 12, "already exsits, terminating.")
            sys.exit(1)
        self.wea = Weather.Weather(self.nb_foyers) # météo => # WARNING  TODO not a proces
        self.pol = Process(target=Politic.Politic, args=(risque_politique,))
        self.econ = Process(target=Economic.Economic, args=(risque_economique,))
        self.managerThread = threading.Thread(target=self.manager, args=())

        self.price = 10
        # prix de l'énergie au temps t
        self.price_t = 10 #prix au temps t-1
        self.speed = speed #vitesse de la simulation

        self.current_consommation = 0 # à calculer en accédant à toutes les consommations des homes
        self.current_production = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie_1 = 0

        self.start_sub()

    def start_sub(self):
        self.pol.start()
        self.econ.start()
        self.managerThread.start()
        for foyer in self.foyers:
            foyer.start()

    # TODO à refaire
    # fait à la va vite sans trop réfléchir
    def calc_production(self, data_cons):
        """
        exec en tant que Thread
        while True:
            regarder les choses qui arrivent en ipcs

        """
        self.current_production += data_cons["prod"]
        self.current_consommation += data_cons["conso"]
        self.total_energie += data_cons["stock"]
        print("Datas : {}".format(data_cons))

    def manager(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            while True:
                data_cons, t = self.mq.receive()
                executor.submit(self.calc_production, ast.literal_eval(data_cons.decode()))


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

    def newDate(self):

        ## Nouvelle date => on augmente la date, on sig nos child

        if (self.date.value >= 0):
            os.kill(self.pol.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
            os.kill(self.econ.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
        self.date.value += 1

        ## On remet à jour nos datas
        self.total_energie_1 = self.total_energie
        self.total_energie = 0
        self.current_production = 0

    def run(self):

        #plt.figure()
        #t= [x for x in range(365)]
        #prix = []
        #energie = []
        while self.date.value < 5 :
            # 1. J'aurais préféré utilisé une mémoire partagée pour la date qui marche pour un tick mais bon on doit passer par des signaux

            print("#####Jour n°{}####".format(self.date.value))
            self.newDate()

            time.sleep(2)#self.sleep

        self.mq.remove()

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


        """
        pool = Pool(os.cpu.count())

        f = tableau de foyers

        process=partial(Fonction a éxécuter, argument1 = arg1, argumentn = argn)
        pool.map(process, f)

        """
