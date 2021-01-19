import Alea
import signal


class Economic(Alea.Alea):
    """Cette classe définit les événements économiques de la simulation

    """

    def __init__(self, risque=2):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            1: ("Stimulus check", -2.0, signal.SIGUSR1),
            2: ("Les soldes mon pote", -5.0, signal.SIGUSR2),
            3: ("Crise de ouf", 6.0, signal.SIGBUS)
        }
        super(Economic, self).__init__(risque=risque, event=event)
