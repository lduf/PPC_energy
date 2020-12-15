# PPC_energy
Projet de PPC - The Energy Market

<hr>

## 1. Objectif du projet:

Le but est d'implémenter une simulation Python prenant avantage du multi-processing et du multi-threading.

Le programme simule le marché de l'énergie : la production d'énergie, la consommation (représentée par des foyers/maisons), les conditions météo et des éléments aléatoires contribuent au prix de l'électricité.

 - les consommateurs peuvent céder leur surplus d'énergie aux consommateurs environnants ou de vendre ce surplus ce qui induit une diminution du prix de l'électricité.
 -  Les foyers ayant besoin d'électricité doivent en acheter (sur le marché) s'ils ne peuvent pas en récupérer à un consommateur environnant (en condition de surplus)
 - Le prix de l'énergie augmente quand la consommation devient plus importante que la consommation
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

  Un foyer est localisé dans une ville, elle même localisée dans un pays. Ce foyer pourra donner de l'énergie seulement aux autre foyer de sa ville.
  Nous avons deux implémentations envisagées pour le don d'énergie :

  1. Soit le don se fait de pair à pair, seulement ici nous avons un problème, si un donneur ne trouve pas de receveur, que fait il de l'énergie restante ? est ce qu'il la detruit ? reste-t-il en attente ?
  2. Soit on passe par un tier, par exemple un mairie qui recevrait tous les dons, et permettant des échanges différerés, et sans bloquer completement le programme.

### Le marché

 Le marché contient la disponibilité de l'énergie, le prix de l'énergie qui fluctue en fonction des conditions (transaction avec les foyers, aléa politiques ou climatiques, …). Le marché sera ```multi-thread``` et s'occupera des transactions (avec les foyers) dans différents threads. De plus, le nombre de transaction simultanée est limité.
 Le marché à une portée mondiale, toutes les villes de tous les payes sont "connectées" au même marché.

### La météo

 La météo et surtout la température fluctue sur la consommation. Quand il fait froid on allume le chauffage, il fait chaud c'est la clim, …
 Les événements météorologiques auront effets à l'échelle d'une ville (dans un même pays, une ville peut être victime d'une canicule alors qu'une autre peut être victime d'une tempête)
 Toutes les villes d'un pays seront soumises à la même loi de température, mais les événement ponctuels et aléatoires seront indépendant à chaque villes.

### La politique

 Des nouvelles lois sur la production d'énergie, des taxes, des tensions géopolitiques, … peuvent apparaitre et ont des conséquences sur la consommation et la production d'énergie.
 Les événements politiques auront effets à l'échelle d'un pays (c'est à dire pour toutes les villes données d'un même pays).
 Par exemple ces derniers pourraient être:

 1. Révolution : tous les homes changent de bord (préférer vendre ou donner, etc)

### Economie

 Des évènements économiques peuvent apparaitre. Des taux de changes, …
 *(à détailler pcq c'est encore flou pour moi)*


### Bug sur l'interprétation de cette phrase :

 >"home and market processes update terminals they are connected to permitting the operator of the simulation to track its progress"

 En gros on a des retours terminal sur home et market ?

### Prix de l'énergie

 <img alt="Calcul du prix de l'énergie" src="/img/calcul_price.png">

## 3. Structuration et implémentation :

### Implémentation

#### Communication

| \         | Foyers | Marché | Météo | Politique | Économie |
| -         | ------ | ------ | ----- | --------- |  ------- |
| **Foyers**    | Message queues     | Message queue        |       |           |          |
| **Marché**    |        |        |       |           |          |
| **Météo**   |        | Shared memory       |  Shared memory     |           |          |
| **Politique** |        |   Signal     |       |           |          |
| **Économie**  |        |    Signal    |       |           |          |

#### Pseudo code

**Main**

  Un fichier principal gère les différentes classes. Il pose les bases de la simulation.

      Main

          [(String, String)] :: Tableau avec les noms des villes et des pays
          [Foyers] :: Listes des foyers de la simulation

          #set de probabilité

          #Répartition géographique
          #1er tirage équiprobable et ensuite le tirage avantage les plus grande villes

**Géographie**

  Nous décidons d'implémenter un système géographique dans notre programme.

Le monde est

        Monde #process

              Int :: date du jour
              Economics :: données économiques mondiale
              [Country] :: liste des pays dans le monde


Les pays

        Country #process

                String :: nom du pays
                [Ville] :: liste des villes dans le pays
                Politics :: Événements politiques de la ville


Les villes

        City #process

              String :: nom de ville
              [Home] :: Liste des foyers de la ville
              Météo :: météo de la ville

              # 1 message queue par ville
              # Dans cette message queue tous les foyers la lise et les foyers qui ont besoin écrivent dans la message queue
              # La lecture de la message queue est systématique.



**Foyers**

Le consommateur et le producteur sont tous les deux des foyers. Un producteur aura un taux de consommation bien plus élevé
Les foyers communiquent entre eux et avec le marché avec des ```message queues```

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
           Double :: prix de l'énergie

           function ::
           calculer à nouveau le prix de l'energie et la quantité d'Energie
           # Cette fonction va être lancée par thread


**Météo**

   On peut suivre un `cos` dilaté pour simuler les saisons. À l'échelle d'un ville

   ![Température en fonction de l'année](/img/temperature.png)

   Plus la température est extrême plus la consommation augmente.

      Weather

          Double :: température
          int :: date permet de définir une température en fonction

          function :: Maxi*cos(4/366*date) + valeurRandom
          exemple de fonction de température :

          Température(x) = 25cos(π+8/366*x)+3cos(x/10)-4cos(x/20)+5
          Les coefficients sont déterminés à l'instanciation de la classe. Pour une ville donnée


   Les processus de météo sont updatés via ```shared memory```


**Politique**

  Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché. À l'échelle d'un pays
  Politique et économie sont des ```child process``` du marché. Ils communiquent via ```signal``` au processus parent.

      Politics




**Économie**

   Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché. À l'échelle mondiale

      Economics
