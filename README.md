# Trashway

Trashway est une plateforme de gestion intelligente des points de collecte de déchets. Elle propose :
- Un backend API (FastAPI) pour la gestion et la collecte des données des bacs à déchets.
- Un dashboard interactif (Streamlit) pour visualiser la simulation et l’historique des collectes.
- Un carte interactive affichant les parcours de collecte.
- Une base de données SQLite pour stocker les informations des bacs.

## Architecture du projet
- **backend/** : API REST (FastAPI)
- **dashboard/** : Interface utilisateur (Streamlit)
- **database/** : Fichiers de base de données et schéma SQL
- **docker-compose.yml** : Orchestration des services backend et dashboard

## Prérequis
- [Docker](https://www.docker.com/) et [Docker Compose](https://docs.docker.com/compose/)

## Installation et lancement avec Docker
1. Clonez le dépôt et placez-vous dans le dossier du projet.
2. Lancez les services avec :
   ```bash
   docker-compose up --build
   ```
3. Accédez :
   - à l’API : [http://localhost:8000/docs](http://localhost:8000/docs)
   - au dashboard : [http://localhost:8501](http://localhost:8501)

## Installation et lancement en local (optionnel)
### Backend (API)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Dashboard
```bash
cd dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

## Base de données et migration
- Le schéma de la base SQLite est défini dans `database/schema.sql`.
- Pour appliquer des migrations (ajout de colonnes), exécutez :
  ```bash
  python migrate_db.py
  ```

## Variables d’environnement principales
- `DATABASE_URL` (backend) : chemin vers la base SQLite (déjà configuré dans docker-compose)
- `BACKEND_URL` (dashboard) : URL de l’API backend

---

Pour toute question, consultez le code ou ouvrez une issue.