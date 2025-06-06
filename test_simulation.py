#!/usr/bin/env python3
# filepath: /home/paulj/esilv/python/projects/trashway/test_simulation.py
"""
Script de test pour valider le fonctionnement de l'API de simulation
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def test_bins_endpoint():
    """Test de l'endpoint bins"""
    print("🧪 Test de l'endpoint /bins/...")
    response = requests.get(f"{BACKEND_URL}/bins/")
    
    if response.status_code == 200:
        bins = response.json()
        print(f"✅ {len(bins)} poubelles trouvées")
        if bins:
            print(f"   Exemple: {bins[0]}")
        return len(bins)
    else:
        print(f"❌ Erreur: {response.status_code}")
        return 0

def test_simulation_creation():
    """Test de création d'une simulation"""
    print("\n🧪 Test de création de simulation...")
    
    payload = {
        "name": "Test Simulation",
        "max_trucks": 2,
        "max_capacity": 150.0,
        "bins_to_collect": 10
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/simulations/", json=payload, timeout=60)
        
        if response.status_code == 200:
            simulation = response.json()
            print(f"✅ Simulation créée avec succès!")
            print(f"   ID: {simulation['id']}")
            print(f"   Distance totale: {simulation.get('total_distance', 0)/1000:.2f} km")
            print(f"   Temps total: {simulation.get('total_time', 0)/3600:.2f} h")
            print(f"   Status: {simulation.get('status')}")
            return simulation
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Timeout - La simulation prend trop de temps")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_simulation_routes(simulation_id):
    """Test de récupération des routes d'une simulation"""
    print(f"\n🧪 Test de récupération des routes pour simulation {simulation_id}...")
    
    response = requests.get(f"{BACKEND_URL}/simulations/{simulation_id}/routes")
    
    if response.status_code == 200:
        routes = response.json()
        print(f"✅ {len(routes)} points de route trouvés")
        
        # Groupe par camion
        trucks = {}
        for route in routes:
            truck_id = route['truck_id']
            if truck_id not in trucks:
                trucks[truck_id] = []
            trucks[truck_id].append(route)
        
        for truck_id, truck_routes in trucks.items():
            total_weight = sum(r['weight'] for r in truck_routes)
            print(f"   Camion {truck_id + 1}: {len(truck_routes)} arrêts, {total_weight:.1f} kg")
        
        return routes
    else:
        print(f"❌ Erreur: {response.status_code}")
        return []

def test_simulations_list():
    """Test de récupération de la liste des simulations"""
    print("\n🧪 Test de récupération de la liste des simulations...")
    
    response = requests.get(f"{BACKEND_URL}/simulations/")
    
    if response.status_code == 200:
        simulations = response.json()
        print(f"✅ {len(simulations)} simulations trouvées")
        for sim in simulations:
            print(f"   #{sim['id']} - {sim['name']} - {sim['status']}")
        return simulations
    else:
        print(f"❌ Erreur: {response.status_code}")
        return []

def main():
    """Fonction principale de test"""
    print("🚀 Début des tests d'intégration Trashway\n")
    
    # Test 1: Vérifier les poubelles
    bins_count = test_bins_endpoint()
    if bins_count == 0:
        print("❌ Aucune poubelle trouvée. Veuillez d'abord initialiser la base de données.")
        return
    
    # Test 2: Créer une simulation
    simulation = test_simulation_creation()
    if not simulation:
        print("❌ Impossible de créer une simulation. Arrêt des tests.")
        return
    
    # Test 3: Récupérer les routes
    routes = test_simulation_routes(simulation['id'])
    
    # Test 4: Lister les simulations
    simulations = test_simulations_list()
    
    print("\n✅ Tous les tests sont terminés!")
    print(f"   Backend URL: {BACKEND_URL}")
    print(f"   Dashboard URL: http://localhost:8501")
    print("\n💡 Vous pouvez maintenant utiliser l'interface web pour:")
    print("   - Réinitialiser la base de données")
    print("   - Configurer et lancer des simulations")
    print("   - Visualiser les routes sur la carte")

if __name__ == "__main__":
    main()
