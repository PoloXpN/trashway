# Utilitaires éventuels pour le dashboard
import math
import json
import requests 
import time
import random
import os
import sqlite3

# Optional imports - these are only needed for the solver functionality
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2
    HAS_ORTOOLS = True
except ImportError:
    HAS_ORTOOLS = False

def getPosition(adresse: str) -> tuple[float, float] :
    # Format voulut : « 10 rue de la Paix, 75002 Paris, France »

    headers = {
        'Host': 'nominatim.openstreetmap.org',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i'
    }
    params = {
        'q': adresse,
        'format': 'json',
        'polygon': 1,
        'addressdetails': 1
    }
    adresse_en_url = str.replace(adresse, ' ', '+')
    retour = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers)
    retour_json = retour.json()
    print(retour_json)
    time.sleep(1)
    try:
        latitude = retour_json[0]["lat"]
        longitude = retour_json[0]["lon"]

        return (latitude, longitude)
    except Exception as e:
        print(e)
        print(adresse_en_url)
        return (0,0)

def getDistance(pos1: tuple[float, float], pos2: tuple[float, float], timeout: int = 5):
    try:
        url = f'http://router.project-osrm.org/route/v1/driving/{pos1[1]},{pos1[0]};{pos2[1]},{pos2[0]}'
        retour_json = requests.get(url, timeout=timeout)
        retour_json.raise_for_status()
        
        # Reduced sleep time from 1 second to 0.2 seconds
        time.sleep(0.2)
        data = retour_json.json()

        if 'routes' not in data or len(data['routes']) == 0:
            raise ValueError("No routes found")

        info = [(a["distance"],a["duration"]) for a in data["routes"] if a["distance"]>0 and a["distance"]<12000]
        if len(info)>0:
            dist = info[0][0]
            duration = info[0][1]
        else:
            print(f"Distance invalide - Generation aleatoire")
            dist = random.randint(10, 2000)
            duration = dist / 5
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"Erreur réseau - Generation aleatoire: {e}")
        dist = random.randint(10, 2000)
        duration = dist / 5
    except Exception as e:
        print(f"Erreur générale - Generation aleatoire: {e}")
        dist = random.randint(10, 2000)
        duration = dist / 5

    return dist, duration

def getEuclideanDistance(pos1: tuple[float, float], pos2: tuple[float, float]):
    """
    Calculate Euclidean distance between two GPS coordinates.
    This is much faster than routing APIs but less accurate for actual travel.
    
    Returns distance in meters and estimated duration in seconds.
    """
    lat1, lon1 = pos1
    lat2, lon2 = pos2
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula for great-circle distance
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in meters
    R = 6371000
    distance = R * c
    
    # Estimate duration assuming average city speed of 30 km/h = 8.33 m/s
    # Add 20% overhead for turns, traffic lights, etc.
    duration = (distance / 8.33) * 1.2
    
    return distance, duration

class Poubelle:
    def __init__(self, id : int, poids : int, available : bool, adresse : str, latitude: float = None, longitude: float = None): # As defined in database
        self.id = id
        self.poids = poids
        self.available = available
        self.adresse = adresse
        self.latitude = latitude
        self.longitude = longitude
    
    def getPosition(self) -> tuple[float, float]:
        if self.latitude is None or self.longitude is None:
            self.latitude, self.longitude = getPosition(self.adresse)
        return (self.latitude, self.longitude)
        
class Camion:
    def __init__(self, capacite : int):
        self.capacite = capacite

class SolverAdapter:
    def __init__(self, poubelles: list[Poubelle], camions: list[Camion], adresse_depot: str):
        if not HAS_NUMPY:
            raise ImportError("numpy is required for SolverAdapter. Install with: pip install numpy")
        if not HAS_ORTOOLS:
            raise ImportError("ortools is required for SolverAdapter. Install with: pip install ortools")
            
        self.poubelles = [poubelle for poubelle in poubelles if poubelle.available]
        self.camions = camions 
        self.adresse_depot = adresse_depot
    
    def generateMatrix(self):
        pos_depot = (self.adresse_depot["latitude"], self.adresse_depot["longitude"])
        
        n = len(self.poubelles) + 1
        distance_matrix = [[0] * n for _ in range(n)]
        duration_matrix = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    dist = 0
                    duration = 0
                else:
                    if i == 0: # 0 est le dépot
                        dist, duration = getDistance(pos_depot, self.poubelles[j-1].getPosition())
                    else:
                        dist, duration = getDistance(self.poubelles[i-1].getPosition(), self.poubelles[j-1].getPosition())
                
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist
                duration_matrix[i][j] = duration *1.5
                duration_matrix[j][i] = duration *1.5
        
        distance_matrix = np.array(distance_matrix)
        duration_matrix = np.array(duration_matrix)
        return distance_matrix, duration_matrix
    
    def getWheightList(self) -> list[int]:
        return [0] + [poubelle.poids for poubelle in self.poubelles]

    def getCapacityList(self) -> list[int]:
        return [camion.capacite for camion in self.camions]
    
    def generateSolverInput(self):
        distance_matrix, duration_matrix = self.generateMatrix()
        demands = self.getWheightList()
        capacities = self.getCapacityList()

        return distance_matrix, duration_matrix, demands, capacities

    def solve_sum_cvrp(self, time_limit_seconds: int = 30):
        distance_matrix, duration_matrix, demands, capacities = self.generateSolverInput()

        n = distance_matrix.shape[0]
        num_vehicles = len(capacities)
        depot = 0

        # Manager et modèle
        manager = pywrapcp.RoutingIndexManager(n, num_vehicles, depot)
        routing = pywrapcp.RoutingModel(manager)

        # Callback distance -> coût
        def distance_callback(from_idx, to_idx):
            from_node = manager.IndexToNode(from_idx)
            to_node = manager.IndexToNode(to_idx)
            return int(distance_matrix[from_node, to_node])
        
        def duration_callback(from_idx, to_idx):
            from_node = manager.IndexToNode(from_idx)
            to_node = manager.IndexToNode(to_idx)
            return int(duration_matrix[from_node, to_node])

        transit_idx = routing.RegisterTransitCallback(distance_callback)
        time_callback_idx = routing.RegisterTransitCallback(duration_callback)
        max_time = 1 * 3600
        routing.AddDimension(
            time_callback_idx,
            0,          # slack max
            max_time,   # capacité (= durée max)
            True,       # fix start à 0
            'Time'
        )
        time_dimension = routing.GetDimensionOrDie('Time')

        routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

        # Dimension charge pour capacité
        def demand_callback(idx):
            node = manager.IndexToNode(idx)
            return demands[node]
        
        demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_idx,
            0,
            capacities,
            True,
            'Load'
        )

        # Paramètres de recherche
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        params.time_limit.seconds = time_limit_seconds

        # Résolution
        solution = routing.SolveWithParameters(params)
        if not solution:
            return None, None, None

        # Extraction des routes et calcul distance totalea
        routes = []
        total_distance = 0
        for v in range(num_vehicles):
            idx = routing.Start(v)
            route = []
            while not routing.IsEnd(idx):
                route.append(manager.IndexToNode(idx))
                next_idx = solution.Value(routing.NextVar(idx))
                total_distance += routing.GetArcCostForVehicle(idx, next_idx, v)
                idx = next_idx
            route.append(depot)
            routes.append(route)
        
        time_dimension = routing.GetDimensionOrDie('Time')
        vehicle_times = []
        for v in range(num_vehicles):
            end_index = routing.End(v)
            t = solution.Value(time_dimension.CumulVar(end_index))
            vehicle_times.append(t)

        best_time = max(vehicle_times)


        return routes, total_distance, best_time

    def extractPath(self, paths):
        new_paths = []
        for path in paths:
            route = []
            route.append(self.adresse_depot)
            for i in path:
                if i != 0:  # 0 is the depot, so we add poubelles for other indices
                    route.append(self.poubelles[i-1])
            route.append(self.adresse_depot)
            new_paths.append(route)
        return new_paths


def compute_distances(backend_url: str = "", batch_size: int = 50, use_euclidean: bool = False):
    """
    Calcule toutes les distances bin-à-bin et remplit la table `distances` dans la BD locale.
    
    Args:
        backend_url: URL du backend (non utilisé pour l'instant)
        batch_size: Nombre de paires à traiter par batch
        use_euclidean: Si True, utilise la distance euclidienne au lieu de l'API routing
    """
    # Determine if we're running in Docker container or locally
    if os.path.exists('/data/trashway.db'):
        db_path = '/data/trashway.db'
        print("Running in Docker container")
    else:
        # Running locally - find the database file
        try:
            cwd = os.getcwd()
            print(f"Running locally. Current working directory: {cwd}")
            
            if 'trashway' in cwd:
                parts = cwd.split('/')
                trashway_index = -1
                for i, part in enumerate(parts):
                    if part == 'trashway':
                        trashway_index = i
                        break
                
                if trashway_index >= 0:
                    root = '/'.join(parts[:trashway_index + 1])
                else:
                    root = "/home/paulj/esilv/python/projects/trashway"
            else:
                root = "/home/paulj/esilv/python/projects/trashway"
                
            db_path = os.path.join(root, "database", "trashway.db")
        except Exception as e:
            print(f"Error resolving database path: {e}")
            db_path = "/home/paulj/esilv/python/projects/trashway/database/trashway.db"
    
    print(f"Database path: {db_path}")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Récupère tous les bins avec leurs coordonnées
    cur.execute("SELECT id, latitude, longitude FROM bins")
    rows = cur.fetchall()
    
    print(f"Found {len(rows)} bins in database")
    if len(rows) == 0:
        print("No bins found in database. Make sure to initialize the database first.")
        conn.close()
        return

    # Check which distances already exist to avoid recalculation
    cur.execute("SELECT COUNT(*) FROM distances")
    existing_count = cur.fetchone()[0]
    print(f"Found {existing_count} existing distance records")

    # Generate all unique pairs
    pairs_to_process = []
    for idx, (id1, lat1, lon1) in enumerate(rows):
        for id2, lat2, lon2 in rows[idx+1:]:
            # Check if this pair already exists
            cur.execute("SELECT COUNT(*) FROM distances WHERE from_id = ? AND to_id = ?", (id1, id2))
            if cur.fetchone()[0] == 0:
                pairs_to_process.append((id1, lat1, lon1, id2, lat2, lon2))

    total_pairs = len(pairs_to_process)
    print(f"Need to process {total_pairs} new distance pairs")

    if total_pairs == 0:
        print("All distances already calculated!")
        conn.close()
        return

    processed = 0
    failed_count = 0
    
    # Process in batches
    for i in range(0, total_pairs, batch_size):
        batch = pairs_to_process[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{(total_pairs + batch_size - 1)//batch_size}")
        
        for id1, lat1, lon1, id2, lat2, lon2 in batch:
            processed += 1
            print(f"Computing distance {processed}/{total_pairs}: bin {id1} to bin {id2}")
            
            try:
                if use_euclidean:
                    dist, duration = getEuclideanDistance((lat1, lon1), (lat2, lon2))
                else:
                    dist, duration = getDistance((lat1, lon1), (lat2, lon2))
                
                # Insère les deux sens
                cur.execute(
                    "INSERT OR REPLACE INTO distances (from_id, to_id, distance_m, duration_s) VALUES (?, ?, ?, ?)",
                    (id1, id2, dist, duration * 1.5)
                )
                cur.execute(
                    "INSERT OR REPLACE INTO distances (from_id, to_id, distance_m, duration_s) VALUES (?, ?, ?, ?)",
                    (id2, id1, dist, duration * 1.5)
                )
                    
            except Exception as e:
                failed_count += 1
                print(f"Error calculating distance between bins {id1} and {id2}: {e}")
                # Use a fallback random distance if the API fails
                dist = random.randint(100, 5000)
                duration = dist / 5
                
                cur.execute(
                    "INSERT OR REPLACE INTO distances (from_id, to_id, distance_m, duration_s) VALUES (?, ?, ?, ?)",
                    (id1, id2, dist, duration * 1.5)
                )
                cur.execute(
                    "INSERT OR REPLACE INTO distances (from_id, to_id, distance_m, duration_s) VALUES (?, ?, ?, ?)",
                    (id2, id1, dist, duration * 1.5)
                )
        
        # Commit after each batch
        conn.commit()
        print(f"Batch completed. Progress: {processed}/{total_pairs} ({processed/total_pairs*100:.1f}%)")
        
        # Add a small delay between batches to be nice to the API
        if not use_euclidean and i + batch_size < total_pairs:
            print("Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    conn.close()
    print(f"\nDistance calculation completed!")
    print(f"Total processed: {processed}")
    print(f"Failed calculations: {failed_count}")
    print(f"Success rate: {(processed-failed_count)/processed*100:.1f}%")


def compute_distances_matrix_batch(backend_url: str = "", max_batch_size: int = 25):
    """
    Calculate distances using matrix API calls for better efficiency.
    Some routing services support matrix APIs that can calculate multiple distances in one call.
    """
    # Database setup
    if os.path.exists('/data/trashway.db'):
        db_path = '/data/trashway.db'
    else:
        cwd = os.getcwd()
        if 'trashway' in cwd:
            parts = cwd.split('/')
            for i, part in enumerate(parts):
                if part == 'trashway':
                    root = '/'.join(parts[:i + 1])
                    break
            db_path = os.path.join(root, "database", "trashway.db")
        else:
            db_path = "/home/paulj/esilv/python/projects/trashway/database/trashway.db"
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT id, latitude, longitude FROM bins")
    bins = cur.fetchall()
    
    print(f"Found {len(bins)} bins")
    
    # Clear existing distances
    cur.execute("DELETE FROM distances")
    
    # Process bins in chunks for matrix API
    chunk_size = min(max_batch_size, len(bins))
    total_processed = 0
    
    for i in range(0, len(bins), chunk_size):
        chunk = bins[i:i + chunk_size]
        print(f"Processing chunk {i//chunk_size + 1}: bins {i} to {min(i + chunk_size - 1, len(bins) - 1)}")
        
        # For this example, we'll use Euclidean distance for the matrix
        # In a real implementation, you could use OSRM's matrix API or similar
        for j, (id1, lat1, lon1) in enumerate(chunk):
            for k, (id2, lat2, lon2) in enumerate(bins):
                if id1 != id2:
                    dist, duration = getEuclideanDistance((lat1, lon1), (lat2, lon2))
                    cur.execute(
                        "INSERT INTO distances (from_id, to_id, distance_m, duration_s) VALUES (?, ?, ?, ?)",
                        (id1, id2, dist, duration * 1.5)
                    )
                    total_processed += 1
        
        conn.commit()
        print(f"Processed {total_processed} distance pairs so far")
    
    conn.close()
    print(f"Matrix calculation completed! Total: {total_processed} distances")

# ...existing code...

if __name__ == "__main__":
    # Example/test code - only runs when script is executed directly
    ville = "Lille"
    code_postal = 59000
    insee = "59350"
    url = "http://overpass-api.de/api/interpreter"
    query = f"""
[out:json][timeout:25];

area
  ["boundary"="administrative"]
  ["ref:INSEE"="{insee}"]
  ["admin_level"="8"]
->.searchArea;

(
  way
    ["addr:housenumber"]
    ["addr:street"]
    ["addr:postcode"]
    ["building"="house"]
    (area.searchArea);
);

out center tags;
"""
    response = requests.post(url, data={'data': query})
    data = response.json()

    houses_data = []
    for element in data["elements"]:
        tags = element.get("tags", {})
        street = tags.get("addr:street")
        number = tags.get("addr:housenumber")
        postcode = tags.get('addr:postcode', str(code_postal))
        center = element.get("center")


        if street and number and center:
            lat = center["lat"]
            lon = center["lon"]
            houses_data.append(
                {
                    "adresse": f"{number} {street}, {postcode} {ville}, France",
                    "latitude": lat,
                    "longitude": lon
                }
            )

    print("Taille dataset:", len(houses_data))
    houses_data = houses_data[:1000]

    depot = houses_data[0]

    poubelles = []
    n=0
    for h_data in houses_data[1:500]:
        poubelles.append(Poubelle(n, random.randint(10,30), True, h_data["adresse"], h_data["latitude"], h_data["longitude"]))
        print(h_data["adresse"], h_data["latitude"], h_data["longitude"])
        n+=1

    camions = []
    camions.append(Camion(300))
    camions.append(Camion(200))

    solver = SolverAdapter(poubelles, camions, depot)

    routes, total_distance, best_time = solver.solve_sum_cvrp()

    print("\n---------------------------")
    print("Temps de l'opération: ", best_time/3600,"h")
    print("Distance parcourue: ", total_distance/1000, "km")
    print("Cout du trajet: ",1.75*total_distance/1000, "€")
    print("Trajet optimal :\n", routes)

    new_routes = solver.extractPath(routes)
    print(new_routes)