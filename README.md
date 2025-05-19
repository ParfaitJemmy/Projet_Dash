# 📊 Analyse Factorielle Discriminante avec Dash

Cette application permet de réaliser une **Analyse Factorielle Discriminante (FDA)** de manière interactive à partir d'un fichier de données. Elle a été développée avec [Dash](https://dash.plotly.com/) pour l’analyse exploratoire et la prédiction supervisée.

---

## 🚀 Fonctionnalités

- ✅ **Upload de données** (au format `.csv` ou `.xlsx`)
- ✅ **Sélection dynamique** de la variable cible (catégorielle) et des variables explicatives (numériques)
- ✅ **Vérification automatique** des types de données (cible qualitative, explicatives quantitatives)
- ✅ **Analyse FDA** avec visualisation des composantes discriminantes (LD1, LD2)
- ✅ **Prédiction supervisée** d’un nouvel individu via formulaire
- ✅ **Affichage des probabilités** de prédiction
- ✅ **Détection des valeurs manquantes** dans les variables sélectionnées
---

## 📁 Structure du projet

Projet_Dash/
├── assets/                     # Fichiers CSS, logos, etc.
├── pages/                      # Pages modulaires de l'application Dash
│   ├── __pycache__/           # Cache Python
│   ├── about.py               # Page "À propos"
│   ├── descriptive_stats.py   # Statistiques descriptives
│   ├── fda.py                 # Analyse discriminante
│   ├── home.py                # Page d'accueil
│   ├── upload.py              # Chargement de fichiers
│   └── visualisation.py       # Graphiques interactifs
├── app.py                     # Lancement principal de l'application
├── Procfile                   # Fichier pour déploiement (Heroku/Render)
├── README.md                  # Ce fichier
├── requirements.txt           # Dépendances Python
└── .gitignore                 # Fichiers à exclure du dépôt

