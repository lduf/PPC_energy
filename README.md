# PPC_energy
Projet de PPC - The Energy Market

<hr>

## 1. Objectif :

Le but est d'implémenter une simulation Python prenant avantage du multi-processing et du multi-threading.

Le programme simule le marché de l'énergie : la production d'énergie, la consommation (représentée par des foyers/maisons), les conditions météo et des éléments aléatoires contribuent au prix de l'électricité.

 - les consommateurs peuvent céder leur surplus d'énergie aux consommateurs environnants ou de vendre ce surplus ce qui induit une diminution du prix de l'électricité.
 -  Les foyers ayant besoin d'électricité doivent en acheter (sur le marché) s'ils ne peuvent pas en récupérer à un consommateur environnant (en condition de surplus)
 - Le prix de l'énergie augmente quand la consommation devient plus importante que la consommation
 - Les changements de température (*que je juge périodique*) impactent la consommation (donc le prix)
 - Des évènements aléatoires (nouvelle lois, explosion d'une centrale, …) peuvent affecter le prix de l'énergie

 ## Implémentation minimale :

 **Les foyers**

  Dans cette simulation, les foyers représentent des producteurs et des consommateurs. Chaque foyer a initialement un taux de production et un taux de consommation qui lui est propre.  
  On permet également aux foyers de stocker une certaine quantité d'énergie. En fonction du prix de l'énergie, les foyers ont une tendance à l'achat ou a la vente (pour remplir leur stockage)
  De plus, dans le cas d'un surplus d'énergie un foyer peut adopté un de ces trois comportement.

  1. Toujours donner le surplus d'énergie
  2. Toujours vendre sur le marché
  3. Vendre si on ne peut pas donner

  Un foyer est localisé dans une ville, elle même localisée dans un pays. Ce foyer pourra donner de l'énergie seulement aux autre foyer de sa ville.

 **Le marché**

 Le marché contient la disponibilité de l'énergie, le prix de l'énergie qui fluctue en fonction des conditions (transaction avec les foyers, aléa politiques ou climatiques, …). Le marché sera ```multi-thread``` et s'occupera des transactions (avec les foyers) dans différents threads. De plus, le nombre de transaction simultanée est limité.
 Le marché à une portée mondiale, toutes les villes de tous les payes sont "connectées" au même marché.

 **La météo**

 La météo et surtout la température fluctue sur la consommation. Quand il fait froid on allume le chauffage, il fait chaud c'est la clim, …
 Les évenements météorologiques auront effets à l'échelle d'une ville (dans un même pays, une ville peut être victime d'une canicule alors qu'une autre peut être victime d'une tempête)

 **La politique**

 Des nouvelles lois sur la production d'énergie, des taxes, des tensions géopolitiques, … peuvent apparaitre et ont des conséquences sur la consommation et la production d'énergie.
 Les évenements politiques auront effets à l'échelle d'un pays (c'est à dire pour toutes les villes données d'un même pays)

 **Economie**

 Des évènements économiques peuvent apparaitre. Des taux de changes, …
 *(à détailler pcq c'est encore flou pour moi)*

 ## Communication inter-process

 **Les foyers**

 Les foyers communiquent entre eux et avec le marché avec des ```message queues```

 **La météo**

 Les processus de météo sont updatés via ```shared memory```

 **Politique et économie**

 Politique et économie sont des ```child process``` du marché. Ils communiquent via ```signal``` au processus parent.


 **Bug sur l'interprétation de cette phrase :**

 >"home and market processes update terminals they are connected to permitting the operator of the simulation to track its progress"

 En gros on a des retours terminal sur home et market ?

 ## Prix de l'énergie

 <img alt="Calcul du prix de l'energie" src="/img/calcul_price.png">

 ## Structuration et implémentation :

 ### Communication

| \         | Foyers | Marché | Météo | Politique | Économie |
| -         | ------ | ------ | ----- | --------- |  ------- |
| **Foyers**    | Message queues     | Message queue        |       |           |          |
| **Marché**    |        |        |       |           |          |
| **Météo**   |        | Shared memory       |  Shared memory     |           |          |
| **Politique** |        |   Signal     |       |           |          |
| **Économie**  |        |    Signal    |       |           |          |


### Implémentation

**Main**

-> Un fichier principal gère les différentes classes. Il pose les bases de la simulation.

      Main

          [(String, String)] :: Tableau avec les noms des villes et des pays
          [Foyers] :: Listes des foyers de la simulation

          #set de probabilité

          #Répartition géographique
          #1er tirage équiprobable et ensuite le tirage avantage les plus grande villes



**Foyers**

-> Le consommateur et le producteur sont tous les deux des foyers. Un producteur aura un taux de consommation bien plus élevé

      Home

          Double :: Taux de consommation
          Double :: Taux de production
          Double :: Capacité de stockage
          Int :: Comportement (1. Donneur, 2. Vente, 3. Vendre si on peut pas donner)
          Double :: argent disponible
          Double :: Energie disponible
          (String, String) :: (Nom de la ville, Nom du pays)

**Marché**

-> Semaphore pour locker les x transactions simultanées

      Market

           [Home] :: Listes des homes
           Int :: temps
           Double :: quantité d'énergie disponible
           Double :: prix de l'énergie


**Météo**

   On peut suivre un `cos` dilaté pour simuler les saisons. À l'échelle d'un ville

   Plus la température est extrême plus la consommation augmente.

      Weather

          Double :: température
          int :: date permet de définir une température en fonction

          function :: Maxi*cos(4/365*date) + valeurRandom


**Politique**

  Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché. À l'échelle d'un pays

      Politics



**Économie**

   Probabilité d'un évènement. Chaque évènement à une probabilité d'apparition et à des conséquences sur le marché. À l'échelle mondiale

      Economics
