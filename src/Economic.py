import Alea

class Economic(Alea.Alea) :
    """Cette classe définit les événements économiques de la simulation
        TODO : créer des événements écon

    """

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            1 : ("Taux de change", 0.5),
            2 : ("Un event random", -0.7)
        }
        super(Economic, self).__init__(risque = risque, event = event)
