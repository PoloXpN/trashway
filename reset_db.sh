#!/bin/bash
# Script de réinitialisation rapide de la base de données Trashway

echo "🗄️ Réinitialisation de la base de données Trashway"
echo "=================================================="

# Arrêter Docker Compose si en cours d'exécution
echo "🐳 Arrêt des conteneurs Docker..."
docker-compose down 2>/dev/null || true

# Supprimer la base de données existante
if [ -f "database/trashway.db" ]; then
    echo "📂 Suppression de la base existante..."
    rm -f database/trashway.db
    echo "✅ Base de données supprimée"
else
    echo "ℹ️  Aucune base de données existante"
fi

# Recréer la base avec le schéma
echo "🔧 Création de la nouvelle base..."
if [ -f "database/schema.sql" ]; then
    sqlite3 database/trashway.db < database/schema.sql
    echo "✅ Base de données recréée"
else
    echo "❌ Erreur: schema.sql introuvable"
    exit 1
fi

# Vérifier les tables
echo "🔍 Vérification des tables..."
sqlite3 database/trashway.db ".tables"

echo ""
echo "🎉 Réinitialisation terminée !"
echo "Vous pouvez redémarrer avec: docker-compose up"
