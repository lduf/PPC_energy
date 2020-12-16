import Alea

class Politic(Alea) :
    """Cette classe définit les événements politiques de la simulation
        TODO : gérer les signaux entre politic et market
        TODO : créer des événements politic

    """

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            100 : ("Guerre", -0.5),
            200 : ("Scandale aux USA", -0.7)
        }
        super(Politic, self).__init__(risque, event)
