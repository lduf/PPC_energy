# PPC_energy
Projet de PPC - The Energy Market

<hr>

## 1. Objectif :

Le but est d'implémenter une simulation Python prenant avantage du multi-processing et du multi-threading.

Le programme simule le marché de l'energie : la production d'énergie, la consommation (représentés par des foyers/maisons), les conditions météo et des éléments aléatoires contribuent au prix de l'électricité.

 - les consommateurs peuvent céder leur surplus d'énergie aux consommateur environnant ou de vendre ce surplus ce qui induit une diminution du prix de l'électricité.
 -  Les foyers ayant besoin d'électricité doivent en acheter (sur le marché) s'ils ne peuvent pas en récupérer à un consommateur environnant (en condition de surplus)
 - Le prix de l'énergie augmente quand la consommation devient plus importante que la consommation
 - Les changements de température (*que je juge périodique*) impactent la consommation (donc le prix)
 - Des évenements aléatoires (nouvelle lois, explosion d'une centrale, …) peuvent affecter le prix de l'énergie
 
 ## Implémentation minimale : 
 
 **Les foyers**
 
  Dans cette simulation, les foyers représentent des producteurs et des consommateurs. Chaque foyer a initialement un taux de production et un taux de consommation qui lui est propre.  
  De plus, dans le cas d'un surplus d'énergie un foyer peut adopté un de ces trois comportement 
  
  1. Toujours donner le surplus d'énergie
  2. Toujours vendre sur le marché
  3. Vendre si on ne peut pas donner
 
 **Le marché**
 
 Le marché contient la disponnibilité de l'énergie, le prix de l'énergie qui fluctue en fonction des conditions (transaction avec les foyers, aléa poliques ou climatiques, …). Le marché sera ```multi-thread``` et s'occupera des transactions (avec les foyers) dans différents threads. De plus, le nombre de transaction simultanée est limité.
 
 **La météo**
 
 La météo et surtout la température fluctue sur la consommation. Quand il fait froid on allume le chauffage, il fait chaud c'est la clim, …
 
 **La politique**
 
 Des nouvelles lois sur la production d'énergie, des taxes, des tensions géopolitiques, … peuvent apparaitre et ont des conséquences sur la consommation et la production d'énergie.
 
 **Economie**
    
 Des évènements économiques peuvent apparaitre. Des taux de changes, …
 *(à détailler pcq c'est encore flou pour moi)*
 
 ## Communication inter-process
 
 **Les foyers**
 
 Les foyers communiquent entre eux et avec le marché avec des ```message queues```
 
 **La météo**
 
 Les processus de météo sont updatés via ```shared memory```
 
 **Politique et économie**
 
 Politique et économie sont des ```child process``` du marché. Ils communiques via ```signal``` au processus parent.
 
 
 **Bug sur l'interprétation de cette phrase :**
 
 "home and market processes update terminals they are connected to permitting the operator of the simulation to track its progress"
 
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
