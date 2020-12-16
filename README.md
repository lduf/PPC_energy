# PPC_energy
Projet de PPC - The Energy Market

<hr>

## 1. Objectif du projet:

Le but est d'implémenter une simulation Python prenant avantage du multi-processing et du multi-threading.

Le programme simule le marché de l'énergie : la production d'énergie, la consommation (représentée par des foyers/maisons), les conditions météo et des éléments aléatoires contribuent au prix de l'électricité.

 - les consommateurs peuvent céder leur surplus d'énergie aux consommateurs environnants ou de vendre ce surplus ce qui induit une diminution du prix de l'électricité.
 -  Les foyers ayant besoin d'électricité doivent en acheter (sur le marché) s'ils ne peuvent pas en récupérer à un consommateur environnant (en condition de surplus)
 - Le prix de l'énergie augmente quand la consommation devient plus importante que la production
 - Les changements de température (*que je juge périodique*) impactent la consommation (donc le prix)
 - Des évènements aléatoires (nouvelle lois, explosion d'une centrale, …) peuvent affecter le prix de l'énergie

## 2. Implémentation voulue:

### Structuration temporelle

Nous décidons de séquencer l'execution de notre programme par journée. Par exemple : la météo de la ville est définie pour la journée. Les transactions entre le marché et les foyers peuvent se faire en continue.

### Les foyers

  Dans cette simulation, les foyers représentent des producteurs et des consommateurs. Chaque foyer a initialement un taux de production et un taux de consommation qui lui est propre.  
  On permet également aux foyers de stocker une certaine quantité d'énergie. En fonction du prix de l'énergie, les foyers ont une tendance à l'achat ou a la vente (pour remplir leur stockage)
  De plus, dans le cas d'un surplus d'énergie un foyer peut adopté un de ces trois comportement.

  1. Toujours donner le surplus d'énergie
  2. Toujours vendre sur le marché
  3. Vendre si on ne peut pas donner

  Un foyer est localisé dans une ville, elle même localisée dans un pays. Ce foyer pourra donner de l'énergie seulement aux autres foyers de sa ville.
  Nous avons deux implémentations envisagées pour le don d'énergie :

  1. Soit le don se fait de pair à pair, seulement ici nous avons un problème, si un donneur ne trouve pas de receveur, que fait il de l'énergie restante ? est ce qu'il la detruit ? reste-t-il en attente ?
  2. Soit on passe par un tier, par exemple un mairie qui recevrait tous les dons, et permettant des échanges différerés, et sans bloquer completement le programme.

### Le marché

 Le marché contient la disponibilité de l'énergie, le prix de l'énergie qui fluctue en fonction des conditions (transaction avec les foyers, aléa politiques ou climatiques, …). Le marché sera ```multi-thread``` et s'occupera des transactions (avec les foyers) dans différents threads. De plus, le nombre de transaction simultanée est limité.
 Le marché à une portée mondiale, tous les foyers ( de toutes les villes de tous les pays) sont "connectés" au même marché.

### La météo

 La météo et surtout la température fluctue sur la consommation. Quand il fait froid on allume le chauffage, il fait chaud c'est la clim, …
 Les événements météorologiques auront effets à l'échelle d'une ville (dans un même pays, une ville peut être victime d'une canicule alors qu'une autre peut être victime d'une tempête)
 Tous les foyers d'une même ville auront donc la même température et les mêmes aléas climatiques. Enfin la température mondiale ne sera pas 100% aléatoire : elle suivra une fonction dont les coefficients seront tirés aléatoirement pour chaque ville.

### La politique

 Des nouvelles lois sur la production d'énergie, des taxes, des tensions géopolitiques, … peuvent apparaitre et ont des conséquences sur la consommation et la production d'énergie.
 Les événements politiques auront effets à l'échelle d'un pays (c'est à dire pour toutes les villes données d'un même pays).
 Par exemple ces derniers pourraient être:

 1. Révolution : tous les foyers changent de bord (préférer vendre ou donner, etc)

### Economie

L'économie est de rang mondiale, elle affectera de la même manière l'ensemble des foyers de la planète.
 Des évènements économiques peuvent apparaitre:

 1. Une crise
 2.

### Bug sur l'interprétation de cette phrase :

 >"home and market processes update terminals they are connected to permitting the operator of the simulation to track its progress"

 En gros on a des retours terminal sur home et market ?
 Gestion de l'affichage sur un terminal extérieur

### Prix de l'énergie

 <img alt="Calcul du prix de l'énergie" src="/img/calcul_price.png">

## 3. Structuration et implémentation :

### Implémentation

#### Communication

**Un signal fils --> père existe-t-il ?**

| \             | Foyers              | Marché                  | Météo              | Politique | Économie | Ville             | Pays              | Monde            |
|:-:|:------:|:-----:|:----:|:-------:|:------:|:-----:|:---:|:-----:|
| **Foyers**    | **Message queue**   | **Message queue**       |       X            |     X     |    X     |        ??         |         X         |        X         |
| **Marché**    |   Shared memory     |           X             |       X            |     X     |    X     |         X         |         X         |        X         |
| **Météo**     | (Via ville signal)  |(-> comm via conso foyer)|       X            |     X     |    X     | **Shared memory** |         X         |        X         |
| **Politique** | (via ville signal)  | **Signal** (via monde)  |       X            |     X     |    X     | (via pays signal) |       signal      | signal (via pays)|
| **Économie**  | (via ville signal)  |   **Signal** (via monde)|       X            |     X     |    X     | (via pays signal) | (via pays monde)  |     signal       |
| **Ville**     |    signal           |           X             |   Shared memory    |     X     |    X     |        X          |         X         |        X         |
| **Pays**      |       X             |           X             |       X            |     X     |    X     |     signal        |         X         |     signal       |
| **Monde**     |       X             |         Signal          |       X            |     X     |    X     |         X         |       signal      |        X         |

![Schéma de la communication de notre simulation](/img/communication_de_la_simulation.png)

#### Pseudo code

**Main**

  Un fichier principal gère les différentes classes. Il pose les bases de la simulation.
  Il lance un thread `Market` et un thread ```Monde```

      Main

          Int :: date du jour
          Market::  marché de l'énergie


**Géographie**

  Nous décidons d'implémenter un système géographique dans notre programme. La répartition sera pseudo aléatoire. Le premier tirage est equiprobable (en terme de pays). Ensuite lors d'un tirage, plus il y a de villes dans un pays donné, plus il est probable que la ville appartienne à ce pays. (On appliquera le même raisonnemnet pour les foyers dans les villes)
*Monde*
Le monde contient plusieurs pays les pays seront lancés en multiprocess

        Monde #process

              Economics :: événements économiques mondiaux
              #pour chaque date, le monde appelle une fonction d'économie
              ex: Economics.alea() -> retourne un aléa qui remonte au market ou descend au foyer
                Si descend à Foyers -> envoie un signal à tous les pays, pour qu'ils transmettent eux mêmes aux villes puis aux foyers
                Si remonte à Market -> envoie un signal à Monde pour qu'il parle à Market

              #Il faut aussi une fonction qui gère la transmission de signal vers le haut ou vers le bas en fonction de la consigne

              [Country] :: liste des pays dans le monde

              [Thread]:: Pool de threads qui exécute des fonctions sur nos pays

*Pays*
Les pays contiennent plusieurs villes, les villes sont lancées en multiprocess. Les événements politiques sont définis à cette échelle. Ainsi tous les foyers de ce pays ont les mêmes aléas politiques.

        Country #process

                Politics :: événements politiques nationaux
                #pour chaque date, le monde appelle une fonction de politique
                ex: Politics.alea() -> retourne un aléa qui remonte au market ou descend au foyer

                #Il faut aussi une fonction qui gère la transmission de signal vers le haut ou vers le bas en fonction de la consigne

                String :: nom du pays
                [Ville] :: liste des villes dans le pays

*Villes*
Les villes contiennent nos foyers, lancé en multiprocess. La météo est définie à cette échelle. Ainsi tous les foyers de cette ville  sont soumis à la même météo. Définition d'une `shared memory` entre la ville et les foyers. La ville informe les foyers du changement de météo par `signal`

        City #process

              String :: nom de ville
              [Home] :: Liste des foyers de la ville
              Météo :: météo de la ville

              #Il faut aussi une fonction qui gère la transmission de signal vers le haut ou vers le bas en fonction de la consigne

              # 1 message queue par ville
              # Dans cette message queue tous les foyers la lise et les foyers qui ont besoin écrivent dans la message queue
              # La lecture de la message queue est systématique.




**Foyers**

Le consommateur et le producteur sont tous les deux des foyers. Un producteur aura un taux de consommation bien plus élevé.  
Les foyers communiquent entre eux et avec le marché avec des ```message queue```

      Home

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
          # communication par message queue interne à la ville pour donner de l'énergie (for free)

**Marché**

Semaphore pour locker les x transactions simultanées.  
Thread interne au marché : des Fred comptables pour accueillir les zoulous de la file d'attente (`message queue`) qui vient des foyers

      Market

           Monde :: Listes des homes
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

**Aléas**

  Cette classe permet de définir ce qu'est un aléa. Est ce qu'il doit remonter au Market ou descendre au Foyers

        Alea

            type :: Market ou Foyers
            tuple :: ("Nom de l'éléa",valeur)

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
          Les coefficients sont déterminés à l'instanciation de la classe. Pour une ville donnée

          function :: function de génération d'un aléa climatique (température):
                return Alea("Foyers", "Température", g(x)) où g(x) est une fonction qui calcule l'incidence de la température sur la consommation (à la hausse ou à la baisse)


   Les processus de météo updatent la ville via ```shared memory```


**Politique**

  Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché ou les foyers. À l'échelle d'un pays
  Politique et économie sont des ```child process``` du marché (ici des child de child). Ils communiquent via ```signal``` au processus parent qui fait remonter l'information.

      Politics

              function :: genAlea -> tire un random entre 0 et 1000000000
                  case 1 : return Alea("Foyers","Révolution", 1)
                  case 2 : return Alea("Market", "Détax", 0.75 )
                  …
                  else return Null




**Économie**

   Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché. À l'échelle mondiale.
   Politique et économie sont des ```child process``` du marché (ici des child de child). Ils communiquent via ```signal``` au processus parent qui fait remonter l'information.

      Economics

              function :: genAlea -> tire un random entre 0 et 1000000000
                  case 1 : return Alea("Market","Crise", -10%)
                  …
                  else return Null

### Autre implémentation possible :

 1 unique process politique / économie / météo qui calcule tout le temps et pour tous les pays/villes.
 En gros le process tourne et calcule des trucs et renvoie la data à celui qui lui demande qqch

## Questions

1. Est ce qu'un signal peut se transmettre du fils au père ?
2. Si on fait de la POO, est ce que l'on doit prendre en compte les relations père fils dans nos communications inter-process ?
3. Est ce que l'on peut thread les villes qui thread le foyers ?
4. Est ce qu'on peut fusionner economie et politiques ?
