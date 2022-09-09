# EnergyConsumptionFL

Il reste la lecture du fichier de config à faire mais sinon le projet marche pour un 
premier cas d'usage très simple : on donne une config FL et il renvoit la consommation énergétique
s'il trouve la config dans sa bdd, sinon il renvoit un message d'erreur pour dire qu'il
faut l'alimenter justement.

Pour alimenter la BDD, il faut que récupérer les logs de la plate-forme FL, donc ça 
dépend de chaque plate-forme (vu qu'on peut pas prendre l'exemple du cas centralisé).
Il faut ajouter les informations récupérées de l'expérience dans le csv dans le 
dossier Computation (NRJ-FL/Simulation/Computation/computation_principal_base.csv).

Un petit script Python devrait suffir pour ça.

Si par contre on souhaite tout de même utiliser des expériences du cas centralisé, le
text template se trouve dans Experiments/Centraliszed/codecarbon_experiment-pytorch_local.py

Lorsque j'aurai du temps libre je l'améliorerai dans le but au final de le rendre 
toujours plus dynamique avec les options de States etc (pour l'instant States est pas
pris en compte, la distance entre les devices pour Network non plus, le temps de 
simulation non plus, juste il donne la consommation énergétique de la config FL s'il
l'a dans sa BDD).