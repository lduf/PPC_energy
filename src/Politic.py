import Alea

class Politic(Alea.Alea) :
    """Cette classe définit les événements politiques de la simulation
        TODO : créer des événements politic

    """

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver

        event = {
            1 : ("Guerre", -0.5),
            2 : ("Scandale aux USA", -0.7)
        }
        super(Politic, self).__init__(risque, event)
