# Maths-photo

Bot discord qui transfère photos postées sur un salon d'un serveur A dans un serveur B en créant un salon par jour, et une catégorie par mois.

## Installation

Testé sous python3.7, doit normalement fonctionner sous 3.6+

Créer un nouveau venv nommé `n_venv` :
```
$ python3 -m venv n_venv
```


L'activer:
```
$ source n_venv/bin/activate
```

Installer les dépendances :
```
$ pip3 install -r requirements.txt
```

Pour le désactiver
```
$ deactivate
```

## Configuration

Les noms des variables d'environnements, se trouvent au début de `bot.py` dans la partie `#Constantes`.

Pour les paramétrer, créer un fichier `.env` sous la forme

```
VAR_1=VALEUR_1
VAR_2=VALEUR_2
```

## Lancer le script

Pour débugger
```
$ python3 bot.py
```

Sinon
```
$ python3 -O bot.py
```

## Prise en main

Une fois le bot en ligne, il transferra automatiquement les images postées dans le salon source vers le serveur de stockage des images. 

Il existe aussi une commande (à poster dans le salon source, sous la syntaxe suivante `!retro <Durée>` qui permet va chercher dans l'historique du salon du tous les message entre maintenant et la date indiqué (temps relatif), et transfère les photos prisent durant cet intervalle, pratique lorsque celui qui gère le bot n'a pas pu suivre un cours !

Examples:
* `$retro 7d` -> Transfère toutes les photos prisent il y a moins d'une semaine
* `$retro 3M` -> Transfère toutes les photos prisent durant les 3 dernières minutes
* `$retro 12H` -> Transfère toutes les photos prisent durant les 12 dernières heures

Pour voir toutes les durées possibles, se référer à [cette fonction](https://github.com/Villemarque/maths-photo/blob/e6da16704b9bdf1f87034cb35ea69b04d1e5f825/bot.py#L118).


Le bot détecte les recoupements (cad les images qui ont déjà étées transferées), il est donc judicieux de toujours bien majorer la durée de l'intervalle pour être certain de ne pas rater quelques photos. 

A l'allumage le bot cherche automatiquement les photos prisent durant les 10 dernières minutes, pratique lorsque celui qui gère le bot arrive en retard ;)

Pour plus de précision ne pas hésiter à regarder le code en détail, il est normalement relativement documenté.

## Autre

Créer un raccourci pour lancer le script : Ouvrir `~/.bashrc`

Ajouter :
```
alias maths= python3 - O ~/<PATH>/bot.py
```
Où `<PATH>` est votre chemin vers `bot.py`

Pour rendre le changement effectif :
```
source ~/.bashrc
```
