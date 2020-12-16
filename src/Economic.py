import Alea

class Economic(Alea) :
    """Cette classe définit les événements politiques de la simulation"""

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            100 : ("Taux de change", 0.5),
            200 : ("Un event random", -0.7)
        }
        super(Economic, self).__init__(risque, event)
