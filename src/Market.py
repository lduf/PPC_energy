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
import queue
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

        self.Enelock = threading.Lock()
        self.fifoLock = threading.Lock()
        self.data_ready = threading.Event()
        self.date = Value('i',-1) #(date du jour) Value pour la shared mémory ('i' pour int)
        self.nb_foyers = nb_foyer
        self.foyers = [threading.Thread(target=Home.Home, args=(i, self.date, )) for i in range(self.nb_foyers)]  #Foyer participant au market
        try:
            self.mq = sysv_ipc.MessageQueue(12, sysv_ipc.IPC_CREX)
        except sysv_ipc.ExistentialError:
            print("Message queue", 12, "already exsits, terminating.")
            sys.exit(1)
        self.wea = Weather.Weather(self.nb_foyers) # météo => # WARNING  TODO not a process
        self.pol = Process(target=Politic.Politic, args=(risque_politique,))
        self.econ = Process(target=Economic.Economic, args=(risque_economique,))
        self.managerThread = threading.Thread(target=self.manager, args=())
        self.handle_dataThread = threading.Thread(target=self.handle_data, args=())
        self.dataQueue = queue.Queue()
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
        self.handle_dataThread.start()
        for foyer in self.foyers:
            foyer.start()

#amené à disparaitre
    def handle_data(self): #Véronique la secrétaire prend la tdolist donnée par Gérard son manager. Elle appelle son armée de Fred comptable qui gère les éléments qu'elle transmets
        #with self.EneLock:
        while True :
            with self.fifoLock:
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    data = self.dataQueue.get()
                    if not "goal" in data :
                        pass #error
                    else :
                        goal = data["goal"]
                        #appeler la bonne fonction TODO : appel à faire automatiquement en fonction du nom donné
                        if goal == "state" :
                            #print("Redirection vers calc
                            executor.submit(self.calc_production(data))
                        if goal == "buy":
                            print("Redirection vers buy à faire")
                            executor.submit(self.buy(data))
                        if goal == "sell":
                            print("Redirection vers sell à faire")
                            executor.submit(self.sell(data))


    # TODO à refaire
    # fait à la va vite sans trop réfléchir BUUGGG peut être besoin de lock l'accès aux datas
    def calc_production(self, data_cons):
        with self.Enelock:
            self.current_production += data_cons["prod"]
            self.current_consommation += data_cons["conso"]
            #self.total_energie += data_cons["stock"]
            print("Fonction éxécutée en Thread :")
            print("Datas : {}\n".format(data_cons))

    def manager(self):#Gérard il écoute sa message queue tout le temps et met à jour la tdolist de véronique
        """
                exec en tant que Thread
                while True:
                    regarder les choses qui arrivent en ipcs

                """

        while True:
            data_cons, t = self.mq.receive() # NB on risque d'avoir qq soucis ici peut être devoir mettre un type < X
            data = ast.literal_eval(data_cons.decode())
            if not "goal" in data:
                pass  # error
            else:
                #with self.fifoLock:
                self.dataQueue.put(data)


    #TODO à refaire

    # fait à la va vite sans trop réfléchir
    def calc_price(self):
        etat_reseau = self.current_consommation / self.current_production # facteur qui augmente au diminue le prix en fonction de l'état de la conso/prod
        etat_alea = (self.pol.current_risque + self.econ.current_risque) #somme des composantes polituqes et économiques
        future_price_t = self.price
        energieTotalFactor = math.log(etat_reseau)/abs(math.log(etat_reseau))
        self.price = self.price_t + 1/100*etat_reseau*self.price_t*energieTotalFactor + etat_alea
        self.price_t = future_price_t


    def buy(self, data):
        with self.Enelock :
            print("{} achète de l'énergie".format(data["id"]))
            self.total_energie -= data["needs"]
            # TODO envoie ACK au foyer ??


    def sell(self, data):
        with self.Enelock :
            print("{} vend de l'énergie".format(data["id"]))
            self.total_energie += data["needs"]
            #TODO envoie d'un ACK au foyer ??


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
            print("État de la dispo de l'énergie : {}".format(self.total_energie))
            self.newDate()
        #TODO mettre en attente jusqu'à ce que toutes les datas de la journée se soient bien déroulées
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
