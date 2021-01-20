# PPC_energy
Projet de PPC - The Energy Market

Note de projet avant implémentation : 

<hr>

## 1. Objectif du projet:

Le but est d'implémenter une simulation Python prenant avantage du multi-processing et du multi-threading.

Le programme simule le marché de l'énergie : la production d'énergie, la consommation (représentée par des foyers/maisons), les conditions météo et des éléments aléatoires contribuent au prix de l'électricité.

 - les consommateurs peuvent céder leur surplus d'énergie aux consommateurs environnants ou de vendre ce surplus ce qui induit une diminution du prix de l'électricité.
 -  Les foyers ayant besoin d'électricité doivent en acheter (sur le marché) s'ils ne peuvent pas en récupérer à un consommateur environnant (en condition de surplus)
 - Le prix de l'énergie augmente quand la consommation devient plus importante que la production
 - Les changements de température impactent la consommation des foyers en énergie (donc le prix de cette dernière)
 - Des évènements aléatoires (politiques, économiques ou météorologiques) peuvent affecter le prix de l'énergie

## 2. Implémentation voulue:

### Structuration temporelle

Nous décidons de séquencer l'execution de notre programme par journées. Par exemple : la météo est définie pour la journée. Les transactions entre le marché et les foyers peuvent se faire en continu.

### Les foyers

  Dans cette simulation, les foyers représentent des producteurs et des consommateurs. Chaque foyer a initialement un taux de production et un taux de consommation qui lui est propre.  
  On permet également aux foyers de stocker une certaine quantité d'énergie. En fonction du prix de l'énergie, les foyers ont une tendance à l'achat ou a la vente (pour remplir leur stockage)
  De plus, dans le cas d'un surplus d'énergie un foyer peut adopté un de ces trois comportement.

  1. Toujours donner le surplus d'énergie (don à un voisin direct (+ ou - 1 par rapport à sa position dans le tableau))
  2. Toujours vendre sur le marché
  3. Vendre si on ne peut pas donner

  Un foyer pourra donner de l'énergie seulement à ses voisins direct
  Implémentation envisagée pour le don d'énergie :
  Don de pair à pair par la message queue, envois de message par les donneurs, tous les foyers verifiant si un message d'un donneur proposant de donner avant d'acheter au m

### Le marché

 Le marché contient la disponibilité de l'énergie, le prix de l'énergie qui fluctue en fonction des conditions (transaction avec les foyers, aléa politiques ou climatiques, …). Le marché sera ```multi-thread``` et s'occupera des transactions (avec les foyers) dans différents threads. De plus, le nombre de transaction simultanée est limité.
 Le marché créé des processus fils : `météo`, `politique` et `économie`. Il lance aussi en multithreading les `Foyers`.

### La météo

 La météo et surtout la température fluctue et influe sur la consommation. Quand il fait froid on allume le chauffage, il fait chaud c'est la clim, …
 Les événements météorologiques utiliseront une `shared memory` partagée avec tous les foyers. Chaque foyer pourra lire sa météo de la journée dans cette mémoire.

### La politique

 Des nouvelles lois sur la production d'énergie, des taxes, des tensions géopolitiques, … peuvent apparaitre et ont des conséquences sur le marché.
 La politique est un processus fils de `market` et communique avec ce dernier via `signal`
 Exemple d'événement :

 1. Attaque du capitole = +7 au prix de l'energie

### Economie

La politique est un processus fils de `market` et communique avec ce dernier via `signal`
Exemple d'événement :

1. Stimulus check = -5 prix de l'energie

### Prix de l'énergie

 <img alt="Calcul du prix de l'énergie" src="/img/calcul_price.png">

## 3. Structuration et implémentation :

### Implémentation

#### Communication

**Un signal fils --> père existe-t-il ?**

| \             | Foyers              | Marché                  | Météo              | Politique | Économie |
|:-:|:------:|:-----:|:----:|:-------:|:------:|
| **Foyers**    |   Message queue     | Message queue           |       X            |     X     |    X     |
| **Marché**    | Message queue       |           X             |       X            |     X     |    X     |
| **Météo**     | Shared memory       |x                        |       X            |     X     |    X     |
| **Politique** | x                   | Signal                  |       X            |     X     |    X     |
| **Économie**  | x                   | Signal                  |       X            |     X     |    X     |


![Schéma de la communication de notre simulation](/img/communication_de_la_simulation.png)

#### Pseudo code

**Main**

  Un fichier principal gère les différentes classes. Il pose les bases de la simulation.
  Il lance un process `Market`

      Main

          Int :: date du jour
          Market::  marché de l'énergie


**Foyers**

Le consommateur et le producteur sont tous les deux des foyers. Un producteur aura un taux de consommation bien plus élevé.  
Les foyers communiquent entre eux et avec le marché avec des ```message queue```.
La message queue foyer peut être pensée comme ça : on accepte les types [position-1, position+1] et on envoie des dons avec son type


      Home

          Int :: N° du foyer (position dans le tableau)
          Double :: Taux de consommation
          Double :: Taux de production
          Double :: Capacité de stockage
          Int :: Comportement (1. Donneur, 2. Vente, 3. Vendre si on peut pas donner)
          Double :: argent disponible
          Double :: Energie disponible

          function buy:: (Si j'ai plus de stock) => Message dans la message queue de la ville pour don

          #si je suis un vendeur
          function sell:: (Si j'ai trop d'énergie => ajoute un message dans la message queue MARKET)

          # Si je suis un donneur
          function give:: (Si trop d'énergie && un message dans la message queue alors je donne)
          # communication par message queue aux foyers voisins en mode 3 ways handshakes :

              message dans message queue ("Type ": position, "Message" : quantité d'énergie à donner)
              Les voisins ACK =>
              ok : le don m'intéresse
                    si dispo => je te l'envoie
                    don plus disponible
              pas ok :
                  je ne te l'envoie pas
                  don dispo

            si on recoit deux pas ok => on peut passer à la suite


Voici le processus pour effectuer un don entre deux foyers :

![Mécanisme de don entre Foyers](/img/don_mecanisme.jpeg)


**Marché**

join() d'une Queue pour attendre les transactions,
Thread interne au marché : des Freds comptables pour accueillir les zoulous de la file d'attente (`message queue`) qui vient des foyers

      Market

           Int :: nombre de foyers
           [Home] :: Listes des homes
           Int :: temps
           Int :: nombre de transaction maximum
           Double :: quantité d'énergie disponible
           Double :: prix de l'énergie en t-1
           Double :: prix de l'énergie

           function ::
           calculer à nouveau le prix de l'energie et la quantité d'Energie
           # Cette fonction va être lancée par thread

           # Il est possible de faire une seule et meme fonction qui gère ça à partir d'un type dans la message queue
           function :: vendre de l'énergie à un foyer (lancé dans un thread)
           function :: acheter de l'énergie à un foyer (lancé dans un thread)

           1=> génération des n foyers
           2 => génération des processus enfant (Politics, Economics, Météo)
           3=> While true : gérer les échanges foyers / (appeler les aléas politics economics et météo(calcul de la température en donnant la date) spleep de k secondes entre chaque appel (pour simuler la durée d'une journée)
           l'éxécution des fonctions du while true se fait dans des threads différents



**Météo**

   On peut suivre un `cos` dilaté pour simuler les saisons. À l'échelle d'une ville

   ![Température en fonction de l'année](/img/temperature.png)

   Plus la température est extrême plus la consommation augmente.

      Weather

          Double :: température
          int :: date permet de définir une température en fonction

          function :: Maxi*cos(4/366*date) + valeurRandom
          exemple de fonction de température :
          Température(x) = 25cos(π+8/366*x)+3cos(x/10)-4cos(x/20)+5
          Les coefficients sont déterminés aléatoirement pour chaque foyers

          function :: function de génération d'un aléa climatique (température):
                température == Température(x)


   Les processus de météo updatent la ville via ```shared memory```


**Politique**

  Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché.
  Politique et économie sont des ```child process``` du marché. Ils communiquent via ```signal``` avec le marché.

      Politics

              function :: genAlea -> tire un random entre 0 et 1000000000
                  case 1 : return ("Révolution", 1)
                  case 2 : return ("Détax", 0.75 )
                  …
                  else return Null


**Économie**

   Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché.
   Politique et économie sont des ```child process``` du marché. Ils communiquent via ```signal``` avec le marché.

      Economics

              function :: genAlea -> tire un random entre 0 et 1000000000
                  case 1 : return ("Crise", -10%)
                  …
                  else return Null
