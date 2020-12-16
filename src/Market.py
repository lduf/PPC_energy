# Market file
import Politic, Economic, Weather, Home

class Market :
    """ Classe market qui gère un peu tout le système
        TODO : créer les processus child pour Politic et Economic (voir pour la communication avec signal)
        TODO : lancer l'execution en multithread des foyers
        TODO : implémenter la message queue entre Home.py et Market.py

    """
    def __init__(self, nb_foyer, risque_politique = 7, risque_economique = 5):

        self.date = 0 #(date du jour)
        self.nb_foyers = nb_foyer
        self.foyers = [Home.Home(i) for i in range(self.nb_foyers)] #Foyer participant au market
        self.wea = Weather.Weather(self.nb_foyers) # météo =>
        self.pol = Politic.Politic(risque_politique)
        self.econ =  Economic.Economic(risque_economique)
        self.price = 0 # prix de l'énergie au temps t
        self.price_t = 0 #prix au temps -1

        self.current_consommation = 0 # à calculer en accédant à toutes les consommations des homes
        self.current_production = 0  # à calculer en accédant à toutes les productions des homes


    def calc_price(self):
        etat_reseau = self.current_consommation / self.current_production # facteur qui augmente au diminue le prix en fonction de l'état de la conso/prod
        etat_alea = (self.pol.current_risque + self.econ.current_risque) #somme des composantes polituqes et économiques
        self.prix = etat_reseau*self.price_t + etat_alea

    def achat(self):
        pass

    def vente(self):
        pass
