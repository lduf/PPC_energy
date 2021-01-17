import random
import sysv_ipc
import sys, os
class Comportement :
    DONNEUR = 1
    VENDEUR = 15
    NEUTRE = 3
    def __init__(self):
        prob = random.randint(0, 100)
        if prob <= 10: #10%
            self.comportement = self.DONNEUR
        elif prob > 10 and prob < 80: #70%
            self.comportement = self.NEUTRE
        else : #20%
            self.comportement = self.VENDEUR
    def taux_conso(self):
        """Permet de retourner un taux de consommation aléatoire basé sur le comportement"""
        return random.randint(80, 700)

    def taux_prod(self):
        """Permet de retourner un taux de consommation aléatoire basé sur le comportement
            Dans l'idée les vendeurs produisent bcp bcp plus
        """
        return self.comportement * random.randint(0,500)

    def stockage(self):
        return self.comportement * random.randint(0,500)/20 * random.randint(3, 10)*(16-self.comportement)

class Home:

    """
        Classe Home simule les foyers qui produisent et qui consomment de l'énergie

        TODO : générer aléatoirement les taux de prod / conso / …
        TODO : implémenter une message queue pour communiquer avec le Market
        TODO : implémenter une shared memory pour mettre à jour la consommation par rapport à la météo
        TODO : implémenter buy, sell, give
    """
    def __init__(self, position, date):
        """Constructeur de notre classe Home"""
        try:
            self.mq = sysv_ipc.MessageQueue(12)
        except sysv_ipc.ExistentialError:
            print("Cannot connect to message queue", 12, ", terminating NOW.")
            sys.exit(1)
        self.ppid = os.getppid()
        self.m = str(self.ppid).encode() #VOIR AVEC MATHIS
        #Idée faire une message queue inter home
        self.position = position
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
        pass
        if self.comportement.comportement == Comportement.DONNEUR:
            self.give(need)
            pass
        if self.comportement.comportement == Comportement.VENDEUR:
            self.sell(need)
            pass
        if self.comportement.comportement == Comportement.NEUTRE:
            if not self.give(need) :
                self.sell(need)
            pass


    def buy(self, need):
        """Fonction d'achat d'énergie sur le market, déclanchée quand la quantité d'énergie dans le stock devient négative"""
        needs = {
            "id": self.position,
            "goal": "buy",
            "needs": need
        }
        m = str(needs).encode()
        self.mq.send(m, self.position)
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
        pass

    def actionMeteo(self):
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

    def setup(self, date):
        while True :
            if(self.date == date.value - 1 and date.value > 0):
                self.update()
                self.send_data()
                #print("Foyer {}, new Date : {} \n".format(self.position, self.date))
            pass




