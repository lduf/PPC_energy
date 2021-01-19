# Market file
import concurrent
import ast
import Politic, Economic, Weather, Home
import time, os, signal, math
import sysv_ipc
from multiprocessing import Process, Value, Pool
import threading
import sys
import concurrent.futures
import queue
import matplotlib.pyplot as plt


class Market:
    """ Classe market qui gère un peu tout le système
        TODO : refaire calc price
        TODO : refaire calc production
    """

    def __init__(self, nb_foyer=4, speed=4, risque_politique=1, risque_economique=1):

        self.Enelock = threading.Lock()
        self.fifoLock = threading.Lock()

        # self.data_ready = threading.Event()  USELESS I GUESS
        self.date = Value('i', -1)  # (date du jour) Value pour la shared mémory ('i' pour int)
        self.nb_foyers = nb_foyer
        self.foyers = [threading.Thread(target=Home.Home, args=(i, self.nb_foyers - 1, self.date,)) for i in
                       range(self.nb_foyers)]  # Foyer participant au market
        try:
            self.mq = sysv_ipc.MessageQueue(12, sysv_ipc.IPC_CREX)
        except sysv_ipc.ExistentialError:
            print("Message queue", 12, "already exsits, terminating.")
            sys.exit(1)
        try:
            self.sm = sysv_ipc.SharedMemory(10, flags=sysv_ipc.IPC_CREX, mode =0o660)
        except sysv_ipc.ExistentialError:
            print("Message queue", 10, "already exsits, terminating.")
            sys.exit(1)
        self.wea = Process(target=Weather.Weather, args=(self.nb_foyers,))
        self.pol = Process(target=Politic.Politic, args=(risque_politique,))
        self.econ = Process(target=Economic.Economic, args=(risque_economique,))
        self.event_list = {
            "economic":{
                30: ("Taux de change", 0.5),
                31: ("Un event random", -0.7),
                10: ("Crise de ouf", -2),
            },
            "politic":{
                14: ("Guerre", -0.5),
                19: ("Scandale aux USA", -0.7),
                13: ("Attaque du capitole", -0.9)
            }
        }
        self.e_current_risque = 0.1
        self.p_current_risque = 0.1

        self.managerThread = threading.Thread(target=self.manager, args=())
        self.handle_dataThread = threading.Thread(target=self.handle_data, args=())

        self.dataQueue = queue.Queue()  # Queue pour vérifier que les threads soient bien finis

        self.price = 10  # prix de l'énergie au temps t
        self.price_1 = 0  # prix au temps t-1
        self.speed = speed  # vitesse de la simulation

        self.current_consommation = 0  # à calculer en accédant à toutes les consommations des homes
        self.current_production = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie = 0  # à calculer en accédant à toutes les productions des homes
        self.total_energie_1 = 0

        self.start_sub()  # on démarre tous les threads

    def start_sub(self):
        self.pol.start()
        self.econ.start()
        self.wea.start()
        self.managerThread.start()
        self.handle_dataThread.start()
        for foyer in self.foyers:
            foyer.start()

    # amené à disparaitre
    def handle_data(
            self):  # Véronique la secrétaire prend la tdolist donnée par Gérard son manager. Elle appelle son armée de Fred comptable qui gère les éléments qu'elle transmets
        # with self.EneLock:
        print("HANDLE DATA IS RUNNING")
        while True:
            # with self.fifoLock:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                data = self.dataQueue.get()
                if "goal" in data:
                    goal = data["goal"]
                    if goal == "state":
                        #print("Redirection vers calc")
                        executor.submit(self.calc_production(data))
                    if goal == "buy":
                        #print("Redirection vers buy à faire")
                        executor.submit(self.buy(data))
                    if goal == "sell":
                        #print("Redirection vers sell à faire")
                        executor.submit(self.sell(data))

    # TODO à refaire
    # fait à la va vite sans trop réfléchir BUUGGG peut être besoin de lock l'accès aux datas
    def calc_production(self, data_cons):
        # with self.Enelock:
        print("\t \t • Calc Prod éxécutée pour {}\n".format(data_cons["id"]))
        self.current_production += data_cons["prod"]
        self.current_consommation += data_cons["conso"]
        # self.total_energie += data_cons["stock"]

        self.dataQueue.task_done()

    def manager(self):  # Gérard il écoute sa message queue tout le temps et met à jour la tdolist de véronique
        """
                exec en tant que Thread
                while True:
                    regarder les choses qui arrivent en ipcs

                """
        while True:
            data_cons, t = self.mq.receive(
                type=-999)  # NB on risque d'avoir qq soucis ici peut être devoir mettre un type < X
            data = ast.literal_eval(data_cons.decode())
            #print("\n DEBUG FRERE : {} \n".format(data))
            if not "goal" in data:
                pass  # error
            else:
                print("Data received {}".format(data))
                # with self.fifoLock:
                self.dataQueue.put(data)
                #print("Taille de ma queue {} : ".format(self.dataQueue.qsize()))

    # TODO à étudier

    def calc_price(self):
        etat_reseau = self.current_consommation / (1+self.current_production)  # facteur qui augmente au diminue le prix en fonction de l'état de la conso/prod
        etat_alea = (self.p_current_risque + self.e_current_risque)  # somme des composantes polituqes et économiques
        future_price_1 = self.price
        energieTotalFactor = 1 #math.log(etat_reseau) / abs(math.log(etat_reseau)) # simulation offre demande
        self.price = self.price_1 + 1 / 100 * etat_reseau * self.price_1 * energieTotalFactor + etat_alea
        self.price_1 = future_price_1

    def buy(self, data):
        # with self.Enelock :
        print(" \t \t • {} achète de l'énergie \n".format(data["id"]))
        needs = data["needs"]
        if needs > self.total_energie:
            ack_energie = self.total_energie  # on envoie tout ce qu'il y a de dispo, tant pis pour les autres LOOOOL
            self.total_energie = 0
        else:
            ack_energie = needs
            self.total_energie -= needs

        # envoie de ACK energie au foyer
        self.mq.send(str(ack_energie).encode(), type=(1000 + data["id"]))
        self.dataQueue.task_done()

    def sell(self, data):
        # with self.Enelock :
        print(" \t \t •{} vend de l'énergie \n".format(data["id"]))
        self.total_energie += data["needs"]
        self.dataQueue.task_done()

    def newDate(self):

        ## Nouvelle date => on augmente la date, on sig nos child
        print("Ceci est une nouvelle date happy new day !")
        if (self.date.value >= 0):
            print("J'envoie des sigusr1 à aléa")
            os.kill(self.pol.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
            os.kill(self.econ.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
            os.kill(self.wea.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
        self.date.value += 1

        ## On remet à jour nos datas
        self.total_energie_1 = self.total_energie
        # self.total_energie = 0
        self.current_production = 0

    def events(self, signum, frame):
        # évenet poli
        if signum in self.event_list["politic"] :
            self.e_current_risque = self.event_list["politic"][signum][1]
            print("p_current_risque :", self.p_current_risque)
        elif signum in self.event_list["economic"]:
            #evenement eco
            self.e_current_risque = self.event_list["economic"][signum][1] #il faut qu'on gère les p_current_riisque aussii
            print("e_current_risque :",self.e_current_risque)
        """if type == 0:
            self.e_current_risque = risque
        elif type == 1:
            self.p_current_risque = risque"""

    def kill(self, signum, frame):
        self.mq.remove()
        self.sm.remove()

    def run(self):

        # plt.figure()
        # t= [x for x in range(365)]
        # prix = []
        # energie = []
        while self.date.value < 10:
            # 1. J'aurais préféré utilisé une mémoire partagée pour la date qui marche pour un tick mais bon on doit passer par des signaux
            print("\n\n\n#####Jour n°{}####".format(self.date.value))
            print("État de la dispo de l'énergie : {}".format(self.total_energie))
            self.newDate()
            print("Prix de l'énergie hier : {}".format(self.price_1))
            print("Prix de l'énergie : {}".format(self.price))
            self.calc_price()
            signal.signal(signal.SIGUSR1, self.events)#je croi s qu'on a pas besoin de le mettre dans un while true
            signal.signal(signal.SIGUSR2, self.events)#je croi s qu'on a pas besoin de le mettre dans un while true
            signal.signal(signal.SIGBUS, self.events)#je croi s qu'on a pas besoin de le mettre dans un while true
            signal.signal(signal.SIGALRM, self.events)#je croi s qu'on a pas besoin de le mettre dans un while true
            signal.signal(signal.SIGCONT, self.events)#je croi s qu'on a pas besoin de le mettre dans un while true
            signal.signal(signal.SIGPIPE, self.events)#je croi s qu'on a pas besoin de le mettre dans un while true
            signal.signal(signal.SIGINT, self.kill)#je croi s qu'on a pas besoin de le mettre dans un while true
            # self.pool.close()
            # self.pool.join()
            time.sleep(1)  # voir doc c'est normal https://docs.python.org/fr/3/library/multiprocessing.html#multiprocessing.Queue
            self.dataQueue.join()
            print("Le wait pool est passé")
            # time.sleep(2)#self.sleep

        self.mq.remove()
        self.sm.remove()

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
