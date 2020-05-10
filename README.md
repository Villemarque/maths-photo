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
