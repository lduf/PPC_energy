import Alea, signal

class Politic(Alea.Alea) :
    """Cette classe définit les événements politiques de la simulation

    """

    def __init__(self, risque=8):
        # Définition des éléments statistiques qui peuvent arriver
        event = {
            4 : ("Guerre", -0.5, signal.SIGALRM),
            5 : ("Scandale aux USA", -0.7, signal.SIGCONT),
            6 : ("Attaque du capitole", -0.9, signal.SIGPIPE)
        }
        super(Politic, self).__init__(risque, event)
