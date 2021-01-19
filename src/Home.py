import ast
import random
import threading

import sysv_ipc
import sys, os
class Comportement :
    DONNEUR = 6
    VENDEUR = 10
    NEUTRE = 3
    def __init__(self):
        prob = random.randint(0, 100)
        if prob <= 50: #10%
            self.comportement = self.DONNEUR
        elif prob > 50 and prob < 80: #70%
            self.comportement = self.NEUTRE
        else : #20%
            self.comportement = self.VENDEUR
    def taux_conso(self):
        """Permet de retourner un taux de consommation aléatoire basé sur le comportement"""
        return 2*random.randint(80, 700)

    def taux_prod(self):
        """Permet de retourner un taux de consommation aléatoire basé sur le comportement
            Dans l'idée les vendeurs produisent bcp bcp plus
        """
        return self.comportement * random.randint(0,500)

    def stockage(self):
        return self.comportement * random.randint(0,500)/20 * random.randint(3, 10)*(self.VENDEUR+1-self.comportement)

class Home:

    """
        Classe Home simule les foyers qui produisent et qui consomment de l'énergie

        TODO : implémenter une shared memory (ou mieux ?) pour mettre à jour la consommation par rapport à la météo
    """
    def __init__(self, position, position_max, date):
        """Constructeur de notre classe Home"""
        try:
            self.sm = sysv_ipc.SharedMemory(10)
        except sysv_ipc.ExistentialError:
            print("Foyer {} Cannot connect to shared Memory 10 terminating NOW. \b {} ".format(position, sysv_ipc.ExistentialError))
            sys.exit(1)
        try:
            self.mq = sysv_ipc.MessageQueue(12)
        except sysv_ipc.ExistentialError:
            print("Cannot connect to message queue", 12, ", terminating NOW.")
            sys.exit(1)


        self.ppid = os.getppid()
        self.m = str(self.ppid).encode() #VOIR AVEC MATHIS
        #Idée faire une message queue inter home
        self.position = position
        self.position_before= self.position -1 if self.position > 0 else position_max
        self.position_after = self.position +1 if self.position < position_max else 0
        self.comportement = Comportement()
        self.taux_consommation = self.comportement.taux_conso()
        self.current_consommation = self.taux_consommation
        self.taux_production = self.comportement.taux_prod()
        self.stockage_max = self.comportement.stockage()
        self.stockage = self.stockage_max/10

        self.state = {
            "conso" : self.current_consommation,
            "prod" : self.taux_production,
            "stock" : self.stockage,
            "id" : self.position
        }
        self.argent = 0

        self.date = 0
        self.temperature = 0

        self.setup(date)

    def send(self, need):
        """Gère l'envoie d'une certaine quantité d'énergie en fonction du critère du foyer (Donneur, vendeur ou neutre"""
        if self.comportement.comportement == Comportement.DONNEUR:
            print("toto donneur")
            self.give(need)
        if self.comportement.comportement == Comportement.VENDEUR:
            self.sell(need)
        if self.comportement.comportement == Comportement.NEUTRE:
            notGiven = self.give(need)
            if notGiven> 0 :
                self.sell(notGiven)


    def buy(self, need):
        """Fonction d'achat d'énergie sur le market, déclanchée quand la quantité d'énergie dans le stock devient négative"""
        needs = {
            "id": self.position,
            "goal": "buy",
            "needs": abs(need)
        }
        m = str(needs).encode()
        self.mq.send(m, self.position)


        ack_energie, type = self.mq.receive(type=(1000+self.position))
        ack_energie = int(ack_energie.decode())
        print(" ———————————— TRANSACTION TRANSALTLANTIQUE OKKKK PELO : {}".format(ack_energie))
        self.stockage += ack_energie
        #pass

    def sell(self, need):
        """Fonction de vente d'énergie sur le market, déclanchée quand la quantité d'énergie dans le stock est supérieur au stockage max"""
        needs = {
            "id": self.position,
            "goal": "sell",
            "needs": need
        }
        m = str(needs).encode()
        self.mq.send(m, self.position)
        #pass

    def give(self, need):
        """Retourne un booléan => TRUE s'il a pu donnner FALSE sinon"""
        print("toto give")
        needs = {
            "id": self.position,
            "goal": "give",
            "needs": abs(need),
            "state": 0
        }
        m = str(needs).encode()
        print("{} envoie un message de type {}".format(self.position,2000+self.position_before))
        print("{} envoie un message de type {}".format(self.position,2000+self.position_after))
        self.mq.send(m, type=(2000+self.position_before))# on envoie la proposition de don à la maison de gauche, type 2000 pour premiere communication
        self.mq.send(m, type=(2000+self.position_after))# on envoie la proposition de don à la maison de droite

    #Peut être que ça merde ici
        mB,tB =  self.mq.receive(type=(3000+self.position)) # type 3000 une fois le contact bien mené
        mA,tA = self.mq.receive(type=(3000+self.position))


        mA = ast.literal_eval(mA.decode())
        mB = ast.literal_eval(mB.decode())

        needs["state"] = 2
        needs["id"]=self.position

        if mA["ack"] > mB["ack"] :
            order = [mA, mB]
        else :
            order = [mB, mA]
        print("Ordre de don : {} ".format(order))
        for i in range(0, len(order)) : #On envoie l'energie qu'on a aux voisins en donnnant en priorité à celui qui en a le plus besoin
            needs["needs"] = min(abs(need), abs(order[i]["ack"]))
            self.mq.send(str(needs).encode(), type=(3000+order[i]["id"]))
            if i < len(order)-1:
                need-=abs(float(needs["needs"]))

        return need

    def handle_giveMessage(self, mess):
        print("•••••• {} veut me donner {}".format(mess["id"], mess["needs"]))
        giver = mess["id"]
        #Prépare un message de réponse
        mess["state"] = 1
        mess["id"] = self.position#VERIF J'ai quelques couilles à cet endroit
        mess["ack"] = self.stockage_max - self.stockage #on répond en donnant le stockage disponnible
        self.mq.send(str(mess).encode(),type=(3000+giver)) #réponse à la proposition

        mGiver,tGiver =  self.mq.receive(type=(3000+self.position))
        mGiver = ast.literal_eval(mGiver.decode())
        print("•••••• Je suis {} et {}  me donne {}".format(self.position, mGiver["id"], mGiver["needs"]))
        self.stockage += mGiver["needs"]


    def actionMeteo(self):
        meteo = eval(self.sm.read().decode())
        self.temperature = meteo[self.position]
        print("Foyer {} : température actuelle : {}".format(self.position, self.temperature))
        self.current_consommation = self.taux_consommation
        if self.temperature <= 0 : self.current_consommation*=1.5
        if self.temperature > 0  and self.temperature <= 12: self.current_consommation*=1.3
        if self.temperature > 12  and self.temperature <= 18: self.current_consommation*=1.15
        if self.temperature > 18  and self.temperature <= 22: self.current_consommation*=1
        if self.temperature > 22  and self.temperature <= 24: self.current_consommation*=0.75
        if self.temperature > 24  and self.temperature <= 30: self.current_consommation*=0.9 #Ventilateurs et clim
        if self.temperature > 30  and self.temperature <= 34: self.current_consommation*=1
        if self.temperature > 34  : self.current_consommation*=1.2

    def update(self):
        self.date+=1
        # TODO récupérer la météo
        self.actionMeteo()
        energie = self.taux_production - self.taux_consommation
        if energie > 0 :
            if self.stockage+energie <= self.stockage_max :
                self.stockage = self.stockage + energie
            else:
                self.send(self.stockage+energie - self.stockage_max)
                self.stockage = self.stockage_max
        else :
            if self.stockage + energie < 0 :
                self.buy(energie)
            else :
                self.stockage = self.stockage + energie #pour soustraire de l'énergie

        self.state["conso"] = self.current_consommation
        self.state["prod"] = self.taux_production
        self.state["stock"] = self.stockage

    def send_data(self):
        state = self.state
        state["goal"] = "state"
        m = str(self.state).encode()
        self.mq.send(m,self.position)

    def giverListen(self):
        while True :
            mess, type = self.mq.receive(type=(2000+self.position))
            mess = ast.literal_eval(mess.decode())
            if "goal" in mess and "state" in mess and mess["state"] == 0:
                threading.Thread(target=self.handle_giveMessage, args=(mess,)).start()

    def setup(self, date):
        threading.Thread(target=self.giverListen, args=()).start()
        while True :
            # on écoute si on a des nouveaux messages

            if(self.date == date.value - 1 and date.value > 0):
                self.update()
                self.send_data()
                #print("Foyer {}, new Date : {} \n".format(self.position, self.date))
            pass




