#!/usr/bin/env python3
# filepath: /home/paulj/esilv/python/projects/trashway/simple_test.py
"""
Script de test simple pour valider le fonctionnement de l'API
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def main():
    print("🚀 Test simple de l'API Trashway\n")
    
    # Test 1: Vérifier les poubelles
    print("🧪 Test de l'endpoint /bins/...")
    response = requests.get(f"{BACKEND_URL}/bins/")
    
    if response.status_code == 200:
        bins = response.json()
        print(f"✅ {len(bins)} poubelles trouvées")
    else:
        print(f"❌ Erreur: {response.status_code}")
        return
    
    # Test 2: Vérifier l'endpoint simulations
    print("\n🧪 Test de l'endpoint /simulations/...")
    response = requests.get(f"{BACKEND_URL}/simulations/")
    
    if response.status_code == 200:
        simulations = response.json()
        print(f"✅ Endpoint simulations OK, {len(simulations)} simulations trouvées")
    else:
        print(f"❌ Erreur: {response.status_code}")
        return
    
    print("\n✅ Tests basiques réussis!")
    print("\n💡 Pour tester les simulations, utilisez l'interface web:")
    print("   🌐 Dashboard: http://localhost:8501")
    print("   📊 API: http://localhost:8000")
    print("\n📝 Instructions:")
    print("   1. Ouvrez le dashboard dans votre navigateur")
    print("   2. Cliquez sur 'Réinitialiser la base de données'")
    print("   3. Configurez les paramètres de simulation")
    print("   4. Lancez une simulation")
    print("   5. Visualisez les résultats sur la carte")

if __name__ == "__main__":
    main()
