#!/usr/bin/env python3
"""
Script de réinitialisation de la base de données Trashway
Ce script supprime la base de données existante et la recrée avec un schéma propre.
"""

import os
import sqlite3
import subprocess
import sys

def reset_database():
    """Réinitialise complètement la base de données"""
    
    # Chemin vers les fichiers
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, "database", "trashway.db")
    schema_path = os.path.join(project_root, "database", "schema.sql")
    
    print("🗄️ Réinitialisation de la base de données Trashway")
    print("=" * 50)
    
    # Étape 1: Supprimer la base de données existante
    if os.path.exists(db_path):
        print(f"📂 Suppression de la base existante: {db_path}")
        os.remove(db_path)
        print("✅ Base de données supprimée")
    else:
        print("ℹ️  Aucune base de données existante trouvée")
    
    # Étape 2: Vérifier que le schéma existe
    if not os.path.exists(schema_path):
        print(f"❌ Erreur: Fichier schema.sql introuvable: {schema_path}")
        sys.exit(1)
    
    # Étape 3: Recréer la base avec le schéma
    print(f"🔧 Création de la nouvelle base avec le schéma: {schema_path}")
    try:
        result = subprocess.run(
            ["sqlite3", db_path], 
            stdin=open(schema_path, 'r'), 
            capture_output=True, 
            text=True,
            check=True
        )
        print("✅ Base de données recréée avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création de la base: {e}")
        sys.exit(1)
    
    # Étape 4: Vérifier les tables créées
    print("🔍 Vérification des tables créées...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"📋 Tables créées: {', '.join([table[0] for table in tables])}")
        print("✅ Réinitialisation terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        sys.exit(1)

def reset_docker_volumes():
    """Réinitialise aussi les volumes Docker si nécessaire"""
    print("\n🐳 Réinitialisation des volumes Docker...")
    
    try:
        # Arrêter les conteneurs
        subprocess.run(["docker-compose", "down"], capture_output=True, check=False)
        
        # Supprimer les volumes (optionnel)
        result = subprocess.run(
            ["docker", "volume", "ls", "-q", "--filter", "name=trashway"], 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            subprocess.run(["docker", "volume", "rm"] + result.stdout.strip().split(), 
                         capture_output=True, check=False)
            print("✅ Volumes Docker supprimés")
        else:
            print("ℹ️  Aucun volume Docker à supprimer")
            
    except Exception as e:
        print(f"⚠️  Avertissement Docker: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Réinitialise la base de données Trashway")
    parser.add_argument("--with-docker", action="store_true", 
                       help="Réinitialise aussi les volumes Docker")
    parser.add_argument("--force", action="store_true", 
                       help="Force la réinitialisation sans confirmation")
    
    args = parser.parse_args()
    
    if not args.force:
        response = input("⚠️  Voulez-vous vraiment réinitialiser la base de données ? (y/N): ")
        if response.lower() not in ['y', 'yes', 'oui']:
            print("❌ Opération annulée")
            sys.exit(0)
    
    reset_database()
    
    if args.with_docker:
        reset_docker_volumes()
    
    print("\n🎉 Réinitialisation complète terminée !")
    print("Vous pouvez maintenant redémarrer l'application avec 'docker-compose up'")
