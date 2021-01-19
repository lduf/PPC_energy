import Alea
import signal


class Politic(Alea.Alea):
    """Cette classe définit les événements politiques de la simulation

    """

    def __init__(self, risque=2):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            4: ("WW3", 10.0, signal.SIGALRM),
            5: ("Scandale aux USA", 3.0, signal.SIGCONT),
            6: ("Attaque du capitole", 6.0, signal.SIGPIPE)
        }
        super(Politic, self).__init__(risque, event)
