import Alea, signal

class Economic(Alea.Alea) :
    """Cette classe définit les événements économiques de la simulation

    """

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            1 : ("Taux de change", 0.5, signal.SIGUSR1),
            2 : ("Un event random", -0.7, signal.SIGUSR2),
            3 : ("Crise de ouf", -2, signal.SIGBUS)
        }
        super(Economic, self).__init__(risque = risque, event = event)
