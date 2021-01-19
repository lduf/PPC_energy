import ast
import random
import threading
import time
import sysv_ipc
import sys
import os


class Comportement:  # classe gérant le comportement des maisons (valeurs d'équilibrage)

    # valeurs déquilibrage pour les proba dêtre vendeur acheteur ou donneur
    DONNEUR = 6
    VENDEUR = 10
    NEUTRE = 3

    def __init__(self):
        prob = random.randint(0, 100)  # on tire un entier aléatoire pour determiner le comportement
        if prob <= 50:  # 10%
            self.comportement = self.DONNEUR
        elif 50 < prob < 80:  # 70%
            self.comportement = self.NEUTRE
        else:  # 20%
            self.comportement = self.VENDEUR

    def taux_conso(self):
        """Permet de retourner un taux de consommation aléatoire
        """
        return 2 * random.randint(80, 700)

    def taux_prod(self):
        """Permet de retourner un taux de production aléatoire basé sur le comportement
            Dans l'idée les vendeurs produisent beaucoup plus (voir les valeurs numériques)
        """
        return self.comportement * random.randint(0, 500)

    def stockage(self):
        """Permet de retourner une valeur de stockage aléatoire mais basée sur le comportement
        """
        return self.comportement * random.randint(0, 500) / 20 * random.randint(3, 10) * (
                    self.VENDEUR + 1 - self.comportement)


class Home:
    """Classe Home simule les foyers qui produisent et qui consomment de l'énergie
    """

    def __init__(self, position, position_max, date):
        """Constructeur de notre classe Home"""
        try:
            self.sm = sysv_ipc.SharedMemory(10)
        except sysv_ipc.ExistentialError:
            print("Foyer {} Cannot connect to shared Memory 10 terminating NOW. \b {} ".format(position,
                                                                                               sysv_ipc.ExistentialError))
            sys.exit(1)
        try:
            self.mq = sysv_ipc.MessageQueue(12)
        except sysv_ipc.ExistentialError:
            print("Cannot connect to message queue", 12, ", terminating NOW.")
            sys.exit(1)
        try:
            self.smSema = sysv_ipc.Semaphore(10)
        except sysv_ipc.ExistentialError:
            print("Méteo Cannot connect to semaphore", 10, ", terminating NOW.")
            sys.exit(1)

        self.ppid = os.getppid()  # pid du père
        self.position = position  # position, id de la maison
        self.position_before = self.position - 1 if self.position > 0 else position_max  # calcul des position des "voisins"
        self.position_after = self.position + 1 if self.position < position_max else 0
        self.comportement = Comportement()  # choix d'un comportement
        self.taux_consommation = self.comportement.taux_conso()  # taux de conso
        self.current_consommation = self.taux_consommation  # consommation actuelle
        self.taux_production = self.comportement.taux_prod()  # taux de prod
        self.stockage_max = self.comportement.stockage()
        self.stockage = self.stockage_max/10

        self.state = {
            "conso": self.current_consommation,
            "prod": self.taux_production,
            "stock": self.stockage,
            "id": self.position
        }
        self.argent = 0

        self.date = 0
        self.temperature = 0

        self.setup(date)

    def send(self, need):
        """
        Gère l'envoie d'une certaine quantité d'énergie en fonction du critère du foyer (Donneur, vendeur ou
        neutre """
        if self.comportement.comportement == Comportement.DONNEUR:
            self.give(round(need, 2))
        if self.comportement.comportement == Comportement.VENDEUR:
            self.sell(round(need, 2))
        if self.comportement.comportement == Comportement.NEUTRE:
            notGiven = self.give(round(need, 2))
            print("$$$$ Not Given Energie : {}".format(notGiven))
            if notGiven > 0:
                self.sell(round(notGiven, 2))

    def buy(self, need):
        """
        Fonction d'achat d'énergie sur le market, déclanchée quand la quantité d'énergie dans le stock devient négative
        """
        needs = {
            "id": self.position,
            "goal": "buy",
            "needs": abs(need)
        }
        m = str(needs).encode()
        self.mq.send(m, self.position)
        ack_energie, type = self.mq.receive(type=(1000 + self.position))
        ack_energie = round(int(float(ack_energie.decode())), 2)
        # print(" ———————————— TRANSACTION TRANSALTLANTIQUE OKKKK PELO : {}".format(ack_energie))
        self.stockage += ack_energie

    def sell(self, need):
        """
        Fonction de vente d'énergie sur le market, déclanchée quand la quantité d'énergie dans le stock est supérieur au stockage max
        """
        needs = {
            "id": self.position,
            "goal": "sell",
            "needs": need
        }
        m = str(needs).encode()
        self.mq.send(m, self.position)

    def give(self, need):
        """Retourne un booléan => TRUE s'il a pu donnner FALSE sinon"""

        needs = {
            "id": self.position,
            "goal": "give",
            "needs": abs(need),
            "state": 0
        }
        m = str(needs).encode()

        self.mq.send(m, type=(
                    2000 + self.position_before))  # on envoie la proposition de don à la maison de gauche, type 2000 pour premiere communication
        self.mq.send(m, type=(2000 + self.position_after))  # on envoie la proposition de don à la maison de droite

        # Peut être que ça merde ici
        mB, tB = self.mq.receive(type=(3000 + self.position))  # type 3000 une fois le contact bien mené
        mA, tA = self.mq.receive(type=(3000 + self.position))

        mA = ast.literal_eval(mA.decode())
        mB = ast.literal_eval(mB.decode())

        needs["state"] = 2
        needs["id"] = self.position
        if "ack" in mA and "ack" in mB:
            if mA["ack"] > mB["ack"]:
                order = [mA, mB]
            else:
                order = [mB, mA]
            print("Ordre de don : {} ".format(order))
            for i in range(0, len(
                    order)):  # On envoie l'energie qu'on a aux voisins en donnnant en priorité à celui qui en a le plus besoin
                needs["needs"] = min(abs(need), abs(order[i]["ack"]))
                self.mq.send(str(needs).encode(), type=(3000 + order[i]["id"]))
                if i < len(order) - 1:
                    need -= abs(float(needs["needs"]))
        else:
            print("Erreur dans un message lors du dons \n A :{} \n B : {} ".format(mA, mB))

        return need

    def handle_giveMessage(self, mess):
        giver = mess["id"]
        # Prépare un message de réponse
        mess["state"] = 1
        mess["id"] = self.position  # VERIF J'ai quelques couilles à cet endroit
        mess["ack"] = round(self.stockage_max - self.stockage, 2)  # on répond en donnant le stockage disponnible

        self.mq.send(str(mess).encode(), type=(3000 + giver))  # réponse à la proposition

        mGiver, tGiver = self.mq.receive(type=(3000 + self.position))
        mGiver = ast.literal_eval(mGiver.decode())
        print("•••••• Je suis {} et {}  me donne {}".format(self.position, mGiver["id"], round(mGiver["needs"], 2)))
        self.stockage += round(mGiver["needs"], 2)

    def actionMeteo(self):
        self.smSema.acquire()
        sm_content = self.sm.read().decode()
        self.smSema.release()
        # print(sm_content)
        try:
            meteo = eval(sm_content)
            self.temperature = meteo[1][self.position]
            print("Affichage des datas de météo".format(meteo))
        except:
            print("ERREUR lors de la conversion en tableau : ")

        # print("Foyer {} : température actuelle : {}".format(self.position, self.temperature))
        self.current_consommation = self.taux_consommation
        if self.temperature <= 0: self.current_consommation *= 1.5
        if 0 < self.temperature <= 12: self.current_consommation *= 1.3
        if 12 < self.temperature <= 18: self.current_consommation *= 1.15
        if 18 < self.temperature <= 22: self.current_consommation *= 1
        if 22 < self.temperature <= 24: self.current_consommation *= 0.75
        if 24 < self.temperature <= 30: self.current_consommation *= 0.9  # Ventilateurs et clim
        if 30 < self.temperature <= 34: self.current_consommation *= 1
        if self.temperature > 34: self.current_consommation *= 1.2

    def update(self):
        self.date += 1
        self.actionMeteo()
        print("$$$$ Température foyer {} : {}".format(self.position, self.temperature))
        energie = round(self.taux_production - self.taux_consommation, 2)
        if energie > 0:
            if self.stockage + energie <= self.stockage_max:
                self.stockage = round(self.stockage + energie, 2)
            else:
                self.send(round(self.stockage + energie - self.stockage_max, 2))
                self.stockage = round(self.stockage_max, 2)
        else:
            if self.stockage + energie < 0:
                self.buy(round(energie, 2))
            else:
                self.stockage = round(self.stockage + energie, 2)  # pour soustraire de l'énergie

        self.state["conso"] = self.current_consommation
        self.state["prod"] = self.taux_production
        self.state["stock"] = self.stockage

    def send_data(self, goal):
        state = self.state
        state["goal"] = goal
        m = str(self.state).encode()
        self.mq.send(m, self.position)

    def giverListen(self):
        while True:
            mess, type = self.mq.receive(type=(2000 + self.position))
            mess = ast.literal_eval(mess.decode())
            if "goal" in mess and "state" in mess and mess["state"] == 0:
                threading.Thread(target=self.handle_giveMessage, args=(mess,)).start()

    def setup(self, date):
        threading.Thread(target=self.giverListen, args=()).start()
        while True:
            if self.date == date.value - 1 and date.value > 0:
                self.send_data(goal="state")
                self.update()
                self.send_data(goal="work_done")
                # print("Foyer {}, new Date : {} \n".format(self.position, self.date))
