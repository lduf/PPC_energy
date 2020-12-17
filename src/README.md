# Fichiers et fonctions
## Aléa
## Economic
## Politic
## Weather
## Home

## Main

``main.py`` est le fichier principal à appeler pour lancer la simulation.  
Il appelle la classe ``Market.py``. À l'appel on y définit les paramètres principaux de la simulation.

Voici un exemple de génération de ``Market``

    market = Market.Market(5,0.25)
    market.run()
    
 À noter que la signature de ``Market`` est la suivante ; ainsi ont peut lancer une simulation avec des paramètres par défauts.
 
    Market(self, nb_foyer=4, speed = 4, risque_politique = 5, risque_economique = 8)
    
## Market

Le gros de la simulation se déroule dans ``Market``

# TODO :