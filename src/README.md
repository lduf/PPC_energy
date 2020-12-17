# Fichiers et fonctions
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

Il y a un tick (qui change la date ; fonctionne avec un ``time.sleep(self.speed)``, ce paramètre est défini au lancement de la simulation.

Créer des processus fils pour `weather`, `economic`, `politic` et échangent avec eux par signal (**surement optimisable**).

Version actuelle : mélange la POO et la PPC => l'instanciation de certaines classes doivent être passé en mode Thread plutôt qu'en classe (notamment avec `Home`).

Le calcul du prix de la version actuel est mauvais (trop volatile)

**Mode graph**

J'ai utilisé une bibliothèque pour dessiner l'évolution du prix en fonction de l'année. 

Pour repasser en mode 'normal' il faut :

- Retirer les trucs où ``plt`` apparaissent
- Décommenter le ``sleep`` et l'affichage des valeurs souhaitées
- Retirer :

        plt.figure()
        t= [x for x in range(365)]
        prix = []
        energie = []
        
     et plus loin dans le code
        
        prix.append(self.price)
        energie.append(self.total_energie)
 
## Home

Home gère les foyers. Il fonctionne sans thread pour l'instant mais le but est que ``Market`` lance son éxécution avec un thread.

Il y a pas mal de taff dedans => toutes les fonctions d'échanges (vente/don/achat) et aussi faire une implémentation statistique pour la production et la consommation       
## Aléa

Aléa est la classe mère de `economic` et ``politic``. C'est dans celle-ci que sont gérés la génération des événements.


## Economic
Economic implémente tout simplement une suite d'aléa de type économique.

## Politic
Politic implémente tout simplement une suite d'aléa de type politique.

## Weather
À la génération du marché, weather génére un tableau de condition initiale (conditioin météorologique).
Chaque foyer correspond à une valeur dans le tableau.

Il faut maintenant faire une ``shared memory`` pour que les foyers puissent récupérer leurs infos de météo (calculée pour une journée à partir des conditions initiales)

# TODO :

``Market.py``

- TODO : lancer l'execution en multithread des foyers
- TODO : implémenter la message queue entre Home.py et Market.py
- TODO : implémenter buy et sell

``Weather.py``

- TODO : implémenter une shared memory avec les foyers
- TODO : réfléchir comment prévenir d'un changement de température

``Home.py``

- TODO : générer aléatoirement les taux de prod / conso / …
- TODO : implémenter une message queue pour communiquer avec le Market
- TODO : implémenter une shared memory pour mettre à jour la consommation par rapport à la météo
- TODO : implémenter buy, sell, give

``Politic.py``

- TODO : créer des événements politic

``Economic.py``

- TODO : créer des événements economic