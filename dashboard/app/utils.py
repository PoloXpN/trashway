# Utilitaires pour le dashboard Trashway
import math
import requests 
import time

# Configuration
OSRM_API_URL = "http://router.project-osrm.org/route/v1/driving"
PARIS_CENTER = [48.8566, 2.3522]
COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']

def get_osrm_route(coordinates_list, timeout=5):
    """
    Récupère une route depuis l'API OSRM
    
    Args:
        coordinates_list: Liste de tuples (lat, lon)
        timeout: Timeout en secondes
    
    Returns:
        dict: Données de route OSRM ou None si erreur
    """
    try:
        # Format coordinates for OSRM API (lon,lat order)
        coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates_list])
        url = f"{OSRM_API_URL}/{coords_str}?overview=full&geometries=geojson"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        if data.get("routes"):
            return data["routes"][0]
        return None
        
    except Exception as e:
        print(f"Erreur OSRM API: {e}")
        return None

def get_distance_duration(pos1, pos2, timeout=5):
    """
    Calcule la distance et durée entre deux points via OSRM
    
    Args:
        pos1: tuple (lat, lon) point de départ
        pos2: tuple (lat, lon) point d'arrivée
        timeout: Timeout en secondes
    
    Returns:
        tuple: (distance_metres, duree_secondes) ou (None, None) si erreur
    """
    route = get_osrm_route([pos1, pos2], timeout)
    if route:
        return route.get("distance"), route.get("duration")
    return None, None

def get_euclidean_distance(pos1, pos2):
    """
    Calcule la distance euclidienne entre deux coordonnées GPS
    Plus rapide que les API de routage mais moins précis pour les trajets réels
    
    Args:
        pos1: tuple (lat, lon) point de départ
        pos2: tuple (lat, lon) point d'arrivée
    
    Returns:
        tuple: (distance_metres, duree_estimee_secondes)
    """
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    
    # Conversion en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Formule de Haversine pour la distance sur une sphère
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Rayon de la Terre en mètres
    R = 6371000
    distance = R * c
    
    # Estimation de durée en supposant une vitesse moyenne urbaine de 30 km/h = 8.33 m/s
    # Ajout de 20% pour les virages, feux, etc.
    duration = (distance / 8.33) * 1.2
    
    return distance, duration

def format_distance(distance_meters):
    """
    Formate une distance en mètres de manière lisible
    
    Args:
        distance_meters: Distance en mètres
        
    Returns:
        str: Distance formatée (ex: "1.23 km" ou "456 m")
    """
    if distance_meters >= 1000:
        return f"{distance_meters/1000:.2f} km"
    else:
        return f"{distance_meters:.0f} m"

def format_duration(duration_seconds):
    """
    Formate une durée en secondes de manière lisible
    
    Args:
        duration_seconds: Durée en secondes
        
    Returns:
        str: Durée formatée (ex: "1h 23min" ou "45min" ou "2min")
    """
    if duration_seconds >= 3600:
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        return f"{hours}h {minutes}min"
    elif duration_seconds >= 60:
        minutes = int(duration_seconds // 60)
        return f"{minutes}min"
    else:
        return f"{duration_seconds:.0f}s"

