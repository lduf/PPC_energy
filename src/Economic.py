import Alea

class Economic(Alea) :
    """Cette classe définit les événements économiques de la simulation
        TODO : gérer les signaux entre economic et market
        TODO : créer des événements écon

    """

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            100 : ("Taux de change", 0.5),
            200 : ("Un event random", -0.7)
        }
        super(Economic, self).__init__(risque, event)
