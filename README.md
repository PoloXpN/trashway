# 🗑️ Trashway

**Trashway** est une plateforme de gestion intelligente des points de collecte de déchets. Elle optimise les tournées de collecte en analysant les données des bacs à déchets (poids, localisation) et propose des parcours optimisés pour les camions de collecte.

## 🚀 Fonctionnalités

- **API REST** (FastAPI) pour la gestion des bacs à déchets et des simulations
- **Dashboard interactif** (Streamlit) avec visualisation des données et cartes
- **Optimisation des tournées** avec calcul des routes optimales
- **Base de données SQLite** pour le stockage des informations
- **Interface de simulation** pour tester différents scénarios de collecte

## 📁 Architecture du projet

```
trashway/
├── backend/           # API REST (FastAPI)
│   ├── app/
│   │   ├── main.py    # Point d'entrée de l'API
│   │   ├── models.py  # Modèles de données
│   │   ├── database.py # Configuration base de données
│   │   └── routers/   # Endpoints API
├── dashboard/         # Interface utilisateur (Streamlit)
│   └── app/
│       ├── main.py    # Dashboard principal
│       └── pages/     # Pages du dashboard
├── database/          # Base de données et schéma
│   ├── schema.sql     # Structure de la DB
│   └── trashway.db    # Base SQLite (générée)
├── docker-compose.yml # Orchestration des services
└── scripts utilitaires (reset_db.sh, migrate_db.py, etc.)
```

## 🛠️ Prérequis

### Option 1 : Avec Docker (Recommandé)
- [Docker](https://www.docker.com/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/) (version 2.0+)

### Option 2 : Installation locale
- Python 3.8+ 
- pip (gestionnaire de paquets Python)

## 🚀 Installation et lancement

### Méthode Docker (Recommandée)

1. **Clonez le projet**
   ```bash
   git clone https://github.com/PoloXpN/trashway.git
   cd trashway
   ```

2. **Initialisez la base de données**
   ```bash
   ./reset_db.sh
   ```

3. **Lancez les services**
   ```bash
   docker-compose up --build
   ```

4. **Accédez aux services**
   - API (documentation Swagger) : [http://localhost:8000/docs](http://localhost:8000/docs)
   - Dashboard : [http://localhost:8501](http://localhost:8501)

## 🗄️ Gestion de la base de données

### Réinitialisation complète
```bash
# Méthode rapide (script shell)
./reset_db.sh

# Méthode avancée (script Python avec options)
python3 reset_database.py --force --with-docker
```

### Migrations
```bash
python3 migrate_db.py
```

### Structure de la base
- **`bins`** : Informations des bacs (localisation, poids, présence)
- **`simulations`** : Simulations de collecte effectuées  
- **`routes`** : Routes optimisées pour chaque simulation
- **`distances`** : Matrice des distances entre bacs

## 🧪 Tests et développement

### Tests des API
```bash
# Test complet des endpoints
python3 test_api.py

# Test des simulations
python3 test_simulation.py
```

### Variables d'environnement
- `DATABASE_URL` (backend) : chemin vers la base SQLite
- `BACKEND_URL` (dashboard) : URL de l'API backend

## 📦 Dépendances principales

### Backend
- **FastAPI** : Framework API moderne
- **SQLAlchemy** : ORM pour la base de données
- **Uvicorn** : Serveur ASGI
- **Pydantic** : Validation des données

### Dashboard  
- **Streamlit** : Framework d'interface utilisateur
- **Folium** : Cartes interactives
- **OR-Tools** : Optimisation des tournées
- **Pandas** : Manipulation des données