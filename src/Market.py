import concurrent
import ast
import Politic, Economic, Weather, Home
import time, os, signal
import sysv_ipc
from multiprocessing import Process, Value
import threading
import sys
import math
import concurrent.futures
import queue
import matplotlib.pyplot as plt

class TimeoutException(Exception):   # custom exception
    pass

class Market:
    """ Classe market qui gère un peu tout le système"""

    def __init__(self, nb_jours=10, nb_foyer=4, speed=4, risque_politique=1, risque_economique=1):  # donées de lancement initiales

        self.nb_jours = nb_jours # nombre des joursde durée de la simul

        self.Enelock = threading.Lock()  # Les deux locks dont on aura besoin
        self.fifoLock = threading.Lock()

        self.date = Value('i', -1)  # (date du jour) Value pour la shared memory ('i' pour int)
        self.nb_foyers = nb_foyer  # Nb de foyers
        self.foyers = [threading.Thread(target=Home.Home, args=(i, self.nb_foyers - 1, self.date,)) for i in range(self.nb_foyers)]  # On lance un thread par foyer participant au market
        try:
            self.mq = sysv_ipc.MessageQueue(12, sysv_ipc.IPC_CREX)  # on lance une ipc  d'id 12
        except sysv_ipc.ExistentialError:
            print("Message queue", 12, "already exsits, terminating.")
            sys.exit(1)
        try:
            self.sm = sysv_ipc.SharedMemory(10, flags=sysv_ipc.IPC_CREX,mode=0o660)  # on lance une ipc memory d'id 10, 0o660 pour droits d'écriture
        except sysv_ipc.ExistentialError:
            print("Message queue", 10, "already exsits, terminating.")
            sys.exit(1)
        try:
            self.smSema = sysv_ipc.Semaphore(10, flags=sysv_ipc.IPC_CREX,mode=0o660)  # on lance un ipc semaphore d'id 10
        except sysv_ipc.ExistentialError:
            print("Semaphore", 10, "already exsits, terminating.")
            sys.exit(1)
        self.smSema.release()  # on libère le semaphore de la shared memory
        self.wea = Process(target=Weather.Weather, args=(self.nb_foyers,))  # un process pour la météo
        self.pol = Process(target=Politic.Politic, args=(risque_politique,))  # un process pour les aléas politiques
        self.econ = Process(target=Economic.Economic, args=(risque_economique,))  # un process pour les aléas éco
        self.event_list = {  # listes des aléas pouvant survenir
            "economic": {
                30: ("Stimulus check", -2.0),
                31: ("Les soldes mon pote", -5.0),
                10: ("Crise de ouf", 6.0),
            },
            "politic": {
                14: ("WW3", 10.0),
                19: ("Scandale aux USA", 3.0),
                13: ("Attaque du capitole", 6.0)
            }
        }
        self.e_current_risque = 0  # les risques initiaux
        self.p_current_risque = 0

        self.managerThread = threading.Thread(target=self.manager, args=())  # un tread pour le manager
        self.handle_dataThread = threading.Thread(target=self.handle_data, args=())  # un thread pour la fonction qui traite les data,

        self.dataQueue = queue.Queue()  # Queue pour vérifier que les threads soient bien finis

        self.price = 30  # prix de l'énergie au temps t
        self.price_1 = 30  # prix au temps t-1
        self.speed = speed  # vitesse de la simulation (donnée en atribut)

        self.current_consommation = 0  # à calculer en accédant à toutes les consommations des homes
        self.current_production = 1  # à calculer en accédant à toutes les productions des homes
        self.total_energie = 1  # à calculer en accédant à toutes les productions des homes
        self.total_energie_1 = 1  # energie totale à t-1

        self.start_sub()  # on démarre tous les threads


    def start_sub(self):  # fonction de démarage
        self.pol.start()  # on démarre nos trois processus fils
        self.econ.start()
        self.wea.start()
        self.managerThread.start()  # on demarre nos deux threads
        self.handle_dataThread.start()
        for foyer in self.foyers:  # on démarre tous les foyers
            foyer.start()

    def handle_data(self): # Véronique la secrétaire prend la tdolist donnée par Gérard son manager. Elle appelle son armée de Fred comptable qui gère les éléments qu'elle transmets
        print("HANDLE DATA IS RUNNING")
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # pool de thread qui tournent en continu pour traiter les data
                # with self.fifoLock:
                data = self.dataQueue.get()  # on sort une data de la queue
                if "goal" in data:  # si la data contient bien une intention
                    goal = data["goal"]  # on demande le but de la data
                    if goal == "state":  # on appelle la bonne fonction en fonction du but voulu
                        executor.submit(self.calc_production(data))
                    if goal == "buy":
                        executor.submit(self.buy(data))
                    if goal == "sell":
                        executor.submit(self.sell(data))
                    if goal == "work_done":
                        self.dataQueue.task_done()#pour la première communicaiton (state qui reste ouverte pour bloquer tant qu'on a pas recu le work_done)
                        self.dataQueue.task_done()# pour le work_done
                        print("~~~ Taches encore en cours : {}".format(self.dataQueue.unfinished_tasks))

    def calc_production(self, data_cons): # Ici on traite les données d'état envoyés par les homes contenant leur production et leur consommation
        # with self.Enelock:
        self.current_production += data_cons["prod"] # on rajoute les composantes des maisons aux données totales
        self.current_consommation += data_cons["conso"]
        print("~~~ Taches encore en cours : {}".format(self.dataQueue.unfinished_tasks))

    def manager(self):  # Gérard il écoute sa message queue tout le temps et met à jour la tdolist de véronique
        """
        exec en tant que Thread
        while True:
        regarder les choses qui arrivent en ipcs
        """

        while True: #on laisse tourner cette boucle
            data_cons, t = self.mq.receive(type=-999)  # on recoit des queues avec un id entre 0 et 999
            data = ast.literal_eval(data_cons.decode()) # on transforme la data en dictionnaire
            if not "goal" in data: # si il n'y a pas de goal dans data ca sent pas bon on recommence la boucle
                pass  # error
            else: # sinon on met la data dans la queue d'execution que handle_data va traiter
                #print("Data received {}".format(data))
                #with self.fifoLock:
                self.dataQueue.put(data)
                # print("Taille de ma queue  {} : ".format(self.dataQueue.qsize()))

    def calc_price(self):
        etat_reseau = self.current_consommation / (self.current_production)  # facteur qui augmente ao diminue le prix en fonction de l'état de la conso/prod
        etat_alea = (self.p_current_risque + self.e_current_risque)  # somme des composantes politiqes et économiques
        future_price_1 = self.price # on indique que le futur prix-1 est le prix actuel
        try:
            total_energie_tour_suivant = (self.total_energie - self.current_consommation + self.current_production)/(self.total_energie) # si > 1 on diminue le prix si < 1 on augmente le prix
            energieTotalFactor = -math.log(total_energie_tour_suivant) / abs(math.log(total_energie_tour_suivant))  # formules pour faire varier le prix de l'energie en fonction de l'état du réseau
        except:
            total_energie_tour_suivant = 1
            energieTotalFactor = 1
        # prendre en compte : self.total_energie par rapport à la demande d'achat :/
        self.price = self.price_1 + (1 / 50) * etat_reseau * self.price_1 * energieTotalFactor + etat_alea # on calcule le nouveau prix
        self.price_1 = future_price_1 # on met bien futur prix-1 dans prix-1
        print("_______________________________________________")
        print("____etat réseau : {} _______".format(etat_reseau))
        print("____current_consommation : {} _______".format(self.current_consommation))
        print("____current_production : {} _______".format(self.current_production))
        print("____total_energie_tour_suivant : {} _______".format(total_energie_tour_suivant))
        print("____energieTotalFactor : {} _______".format(energieTotalFactor))
        print("____ Modulataion du prix : {} _______".format((1 / 50) * etat_reseau * self.price_1 * energieTotalFactor))
        print("_______________________________________________")

    def buy(self, data): #fonction qui gère les achats
        # with self.Enelock :
        #print(" \t \t • {} achète de l'énergie \n".format(data["id"]))
        needs = data["needs"] # on stock la valeur demandée
        if needs > self.total_energie: # si le foyer demande plus d'energie qu'il y en a de dispo alors -->
            ack_energie = self.total_energie  # on envoie tout ce qu'il y a de dispo, tant pis pour les autres
            self.total_energie = 0 # et on met donc l'energie totale à 0, il a tout pris l'egoïste
        else: # si tout va bien
            ack_energie = needs # on stock la valeur demandée dans un ack qu'on renverra au foyer (three way handshake)
            self.total_energie -= needs # on retire donc la quantité d'energie achetée de l'energie totale que dispose le marché

        # envoie de ACK energie au foyer
        self.mq.send(str(ack_energie).encode(), type=(1000 + data["id"]))  # queue vers les foyers
        self.dataQueue.task_done() # on indique qu'on à t
        print("~~~ Taches encore en cours : {}".format(self.dataQueue.unfinished_tasks))

    def sell(self, data): # gestion de a vente
        # with self.Enelock: # lock pour la valeur de l'energie
        #print(" \t \t •{} vend de l'énergie \n".format(data["id"]))
        self.total_energie += data["needs"] # on rajoute à l'energie totale ce que la maison nous a vendu
        self.dataQueue.task_done() # on valide une action
        print("~~~ Taches encore en cours : {}".format(self.dataQueue.unfinished_tasks))

    def newDate(self):
        # Nouvelle date => on augmente la date, on sig nos child
        if (self.date.value >= 0):
            os.kill(self.pol.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
            os.kill(self.econ.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
            os.kill(self.wea.pid, signal.SIGUSR1)  # on va envoyer nos signaux pour traiter dans les process
        self.date.value += 1 # on incrémente la date

        ## On remet à jour nos datas
        self.total_energie_1 = self.total_energie
        self.current_production = 1
        self.current_consommation = 0

    def events(self, signum, frame): # gestion des evenements recu par les alea (en sig)
            # évent poli
        if signum in self.event_list["politic"]:
            self.e_current_risque = self.event_list["politic"][signum][1] # on recupère le risque
            #print("p_current_risque :", self.p_current_risque)
        elif signum in self.event_list["economic"]:
            # event eco
            self.e_current_risque = self.event_list["economic"][signum][1] # on récupère le risque
            #print("e_current_risque :", self.e_current_risque)
        """if type == 0:
            self.e_current_risque = risque
        elif type == 1:
            self.p_current_risque = risque"""

    def timeout_handler(self, signum, frame):  # raises exception when signal sent
        raise TimeoutException

    def kill(self, signum, frame): # fonction pour kill les ipc (plus pratique que remove à la main)
        self.pol.terminate()  # on kill nos trois processus fils
        self.econ.terminate()
        self.wea.terminate()
        #self.managerThread.terminate()  # on kill nos deux threads
        #self.handle_dataThread.terminate()
        #for foyer in self.foyers:  # on kill tous les foyers
            #foyer.
        self.mq.remove()
        self.sm.remove()
        self.smSema.remove()

    def run(self):
        # on indique que l'on lance events quand on recoit l'un de ces signaux
        signal.signal(signal.SIGUSR1, self.events)
        signal.signal(signal.SIGUSR2, self.events)
        signal.signal(signal.SIGBUS, self.events)
        signal.signal(signal.SIGTRAP, self.events)
        signal.signal(signal.SIGCONT, self.events)
        signal.signal(signal.SIGPIPE, self.events)
        signal.signal(signal.SIGINT, self.kill)  # lance kill sur le Ctrl+c
        signal.signal(signal.SIGALRM, self.timeout_handler)  # lance kill sur le Ctrl+c
        t = []
        price = []
        while self.date.value < self.nb_jours:  # fait tourner la simul sur nb_jour
            print("\n\n\n#####Jour n°{}####".format(self.date.value))

            print("État de la dispo de l'énergie : {}".format(self.total_energie))
            self.newDate()  # on passe à une nouvelle journée (au premier tout on est à j-1)
            print("Prix de l'énergie J-1 : {}".format(self.price_1))
            print("Prix de l'énergie : {}".format(self.price))
            print("\n\n")

            time.sleep(2)  # voir doc c'est normal https://docs.python.org/fr/3/library/multiprocessing.html#multiprocessing.Queue
            signal.alarm(3)
            try:
                self.dataQueue.join()  # on join la data queue (contenant les intructions à effectuer), ainsi on wait que toutes les instructions soient passées
            except TimeoutException:
                #self.dataQueue.clear()
                try :
                    [self.dataQueue.task_done() for _ in range(self.dataQueue.unfinished_tasks)]
                except :
                    pass
                pass
            self.calc_price()  # on calcule le nouveau prix de l'energie
            t.append(self.date.value)
            price.append(self.price)
            print("Le wait pool est passé")
            # time.sleep(1)#self.sleep

        # quelques remove pour la route
        self.mq.remove()
        self.sm.remove()
        self.smSema.remove()
        print("Plotting with : {} \n {}".format(t, price))
        plt.figure()
        plt.title("Évolution du prix au cours du temps")
        plt.grid(True)
        plt.plot(t, price)
        plt.show()

