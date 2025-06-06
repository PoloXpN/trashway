import streamlit as st
import requests
import random
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils import OSRM_API_URL, PARIS_CENTER, COLORS, format_distance, format_duration

st.title("🚛 Simulation de collecte optimisée")

backend_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")
external_api = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/adresse_paris/records?limit=50"

# Section 1: Reset des poubelles
st.header("📍 Gestion des poubelles")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Réinitialiser la base de données", type="primary"):
        with st.spinner("Chargement et insertion des poubelles..."):
            try:
                # Clear existing bins first
                resp = requests.get(f"{backend_url}/bins/")
                if resp.status_code == 200:
                    bins = resp.json()
                    for bin_data in bins:
                        requests.delete(f"{backend_url}/bins/{bin_data['id']}")
                
                # Fetch new data from Paris API
                resp = requests.get(external_api)
                resp.raise_for_status()
                data = resp.json().get("results", [])
                
                count = 0
                for rec in data:
                    geom_x_y = rec.get("geom_x_y", {})
                    lon = geom_x_y.get("lon") if geom_x_y else None
                    lat = geom_x_y.get("lat") if geom_x_y else None
                    
                    if lon and lat:  # Only add bins with valid coordinates
                        payload = {
                            "bin_id": f"bin-{rec.get('objectid')}",
                            "weight": round(random.uniform(10.0, 95.0), 2),  # Random weight
                            "presence": 1,
                            "longitude": lon,
                            "latitude": lat
                        }
                        response = requests.post(f"{backend_url}/bins/", json=payload)
                        if response.status_code == 200:
                            count += 1
                
                st.success(f"✅ {count} poubelles initialisées avec succès!")
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

with col2:
    if st.button("📊 Voir l'état actuel"):
        try:
            resp = requests.get(f"{backend_url}/bins/")
            if resp.status_code == 200:
                bins = resp.json()
                if bins:
                    total_bins = len(bins)
                    total_weight = sum(bin_data.get('weight', 0) for bin_data in bins)
                    avg_weight = total_weight / total_bins if total_bins > 0 else 0
                    
                    col1_stat, col2_stat, col3_stat = st.columns(3)
                    with col1_stat:
                        st.metric("Poubelles", total_bins)
                    with col2_stat:
                        st.metric("Poids total", f"{total_weight:.1f} kg")
                    with col3_stat:
                        st.metric("Poids moyen", f"{avg_weight:.1f} kg")
                else:
                    st.info("Aucune poubelle en base")
        except Exception as e:
            st.error(f"Erreur: {e}")

# Section 2: Configuration de la simulation
st.header("⚙️ Configuration de la simulation")

col1, col2, col3 = st.columns(3)

with col1:
    max_trucks = st.number_input("🚛 Nombre max de camions", min_value=1, max_value=10, value=3)

with col2:
    max_capacity = st.number_input("⚖️ Capacité max par camion (kg)", min_value=50.0, max_value=1000.0, value=200.0, step=10.0)

with col3:
    bins_to_collect = st.number_input("🗑️ Nombre de poubelles à collecter", min_value=0, max_value=50, value=20)
    if bins_to_collect == 0:
        st.caption("0 = toutes les poubelles")

# Initialize simulation name in session state if not exists
if 'simulation_name' not in st.session_state:
    st.session_state.simulation_name = f"Simulation_{random.randint(1000, 9999)}"

col1_name, col2_name = st.columns([3, 1])
with col1_name:
    simulation_name = st.text_input("📝 Nom de la simulation", value=st.session_state.simulation_name)
with col2_name:
    st.write("")  # Empty space for alignment
    if st.button("🔄 Nouveau nom"):
        st.session_state.simulation_name = f"Simulation_{random.randint(1000, 9999)}"
        st.rerun()

# Update session state if user manually changed the name
if simulation_name != st.session_state.simulation_name:
    st.session_state.simulation_name = simulation_name

# Section 3: Lancement de la simulation
st.header("🚀 Simulation")

if st.button("▶️ Démarrer la simulation", type="primary"):
    if not simulation_name.strip():
        st.error("Veuillez donner un nom à la simulation")
    else:
        with st.spinner("Calcul des routes optimisées..."):
            try:
                payload = {
                    "name": simulation_name,
                    "max_trucks": max_trucks,
                    "max_capacity": max_capacity,
                    "bins_to_collect": bins_to_collect
                }
                
                # Start simulation
                response = requests.post(f"{backend_url}/simulations/", json=payload)
                
                if response.status_code == 200:
                    simulation_result = response.json()
                    st.session_state.current_simulation = simulation_result['id']
                    
                    # Display results
                    st.success("✅ Simulation terminée!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Distance totale", format_distance(simulation_result.get('total_distance', 0)))
                    with col2:
                        st.metric("Temps total", format_duration(simulation_result.get('total_time', 0)))
                    with col3:
                        st.metric("Status", simulation_result.get('status', 'unknown'))
                
                else:
                    st.error(f"Erreur lors de la simulation: {response.text}")
                    
            except Exception as e:
                st.error(f"Erreur: {e}")

# Section 4: Historique des simulations
st.header("📋 Historique des simulations")

try:
    resp = requests.get(f"{backend_url}/simulations/")
    if resp.status_code == 200:
        simulations = resp.json()
        
        if simulations:
            # Create a dataframe for better display
            sim_data = []
            for sim in simulations:
                sim_data.append({
                    'ID': sim['id'],
                    'Nom': sim['name'],
                    'Camions max': sim['max_trucks'],
                    'Capacité max': f"{sim['max_capacity']} kg",
                    'Poubelles': sim['bins_to_collect'],
                    'Distance': f"{sim['total_distance']/1000:.2f} km" if sim['total_distance'] else "N/A",
                    'Temps': f"{sim['total_time']/3600:.2f} h" if sim['total_time'] else "N/A",
                    'Status': sim['status'],
                    'Date': sim['created_at'][:16].replace('T', ' ')
                })
            
            df = pd.DataFrame(sim_data)
            st.dataframe(df, use_container_width=True)
            
            # Simulation selection for visualization
            selected_sim_id = st.selectbox(
                "Sélectionner une simulation pour visualisation:",
                options=[sim['id'] for sim in simulations],
                format_func=lambda x: f"#{x} - {next(s['name'] for s in simulations if s['id'] == x)}"
            )
            
            if selected_sim_id:
                st.session_state.current_simulation = selected_sim_id
                
        else:
            st.info("Aucune simulation trouvée")
except Exception as e:
    st.error(f"Erreur lors du chargement des simulations: {e}")

# Section 5: Visualisation sur carte
if hasattr(st.session_state, 'current_simulation') and st.session_state.current_simulation:
    st.header("🗺️ Visualisation des routes")
    
    # Use cache to avoid reloading routes unnecessarily
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_simulation_routes(simulation_id):
        routes_resp = requests.get(f"{backend_url}/simulations/{simulation_id}/routes")
        if routes_resp.status_code == 200:
            return routes_resp.json()
        return None
    
    try:
        # Get routes for selected simulation (cached)
        routes = get_simulation_routes(st.session_state.current_simulation)
        
        if routes:
            # Cache the map creation to avoid regenerating it on every interaction
            @st.cache_data(ttl=300)
            def create_routes_map(simulation_id, routes_data):
                # Create folium map centered on Paris
                m = folium.Map(location=PARIS_CENTER, zoom_start=12)
                
                # Define colors for different trucks
                colors = COLORS
                
                # Group routes by truck
                trucks = {}
                for route in routes_data:
                    truck_id = route['truck_id']
                    if truck_id not in trucks:
                        trucks[truck_id] = []
                    trucks[truck_id].append(route)
                
                # Add routes to map with real street routing
                for truck_id, truck_routes in trucks.items():
                    color = colors[truck_id % len(colors)]
                    
                    # Sort by bin_order
                    truck_routes.sort(key=lambda x: x['bin_order'])
                    
                    # Add markers for each bin
                    for i, route in enumerate(truck_routes):
                        icon_color = 'white' if i == 0 else color
                        icon = 'play' if i == 0 else 'stop'
                        
                        folium.Marker(
                            [route['latitude'], route['longitude']],
                            popup=f"Camion {truck_id+1}<br/>Ordre: {route['bin_order']+1}<br/>Poids: {route['weight']:.1f}kg",
                            tooltip=f"Camion {truck_id+1} - Étape {route['bin_order']+1}",
                            icon=folium.Icon(color=color, icon=icon, icon_color=icon_color)
                        ).add_to(m)
                    
                    # Add real street routes using OSRM
                    if len(truck_routes) > 1:
                        try:
                            # Prepare coordinates for OSRM API
                            coordinates = ";".join([
                                f"{route['longitude']},{route['latitude']}" 
                                for route in truck_routes
                            ])
                            
                            # Call OSRM API for real route geometry
                            osrm_url = f"{OSRM_API_URL}/{coordinates}?overview=full&geometries=geojson"
                            osrm_response = requests.get(osrm_url)
                            
                            if osrm_response.status_code == 200:
                                osrm_data = osrm_response.json()
                                if osrm_data.get("routes"):
                                    route_geom = osrm_data["routes"][0]["geometry"]["coordinates"]
                                    route_distance = osrm_data["routes"][0]["distance"]
                                    route_duration = osrm_data["routes"][0]["duration"]
                                    
                                    # Convert coordinates for Folium (swap lon/lat)
                                    route_coords_folium = [[point[1], point[0]] for point in route_geom]
                                    
                                    # Add real route polyline
                                    popup_text = f"Camion {truck_id+1}<br/>Distance: {route_distance/1000:.2f} km<br/>Durée: {route_duration/60:.1f} min"
                                    folium.PolyLine(
                                        locations=route_coords_folium,
                                        color=color,
                                        weight=4,
                                        opacity=0.8,
                                        popup=folium.Popup(popup_text, max_width=250)
                                    ).add_to(m)
                                else:
                                    # Fallback to straight lines if OSRM fails
                                    route_coords = [[route['latitude'], route['longitude']] for route in truck_routes]
                                    folium.PolyLine(
                                        route_coords,
                                        color=color,
                                        weight=3,
                                        opacity=0.6,
                                        popup=f"Route Camion {truck_id+1} (ligne droite)"
                                    ).add_to(m)
                            else:
                                # Fallback to straight lines if API call fails
                                route_coords = [[route['latitude'], route['longitude']] for route in truck_routes]
                                folium.PolyLine(
                                    route_coords,
                                    color=color,
                                    weight=3,
                                    opacity=0.6,
                                    popup=f"Route Camion {truck_id+1} (ligne droite)"
                                ).add_to(m)
                                
                        except Exception as e:
                            # Fallback to straight lines if any error occurs
                            route_coords = [[route['latitude'], route['longitude']] for route in truck_routes]
                            folium.PolyLine(
                                route_coords,
                                color=color,
                                weight=3,
                                opacity=0.6,
                                popup=f"Route Camion {truck_id+1} (ligne droite)"
                            ).add_to(m)
                
                return m
            
            # Create the map using cached function
            map_obj = create_routes_map(st.session_state.current_simulation, routes)
            
            # Display map with key parameter for stability
            map_data = st_folium(
                map_obj, 
                width=700, 
                height=500,
                key=f"simulation_map_{st.session_state.current_simulation}"
            )
                
            # Display route details
            st.subheader("📋 Détails des routes")
            
            # Group routes by truck for details display
            trucks = {}
            for route in routes:
                truck_id = route['truck_id']
                if truck_id not in trucks:
                    trucks[truck_id] = []
                trucks[truck_id].append(route)
            
            for truck_id, truck_routes in trucks.items():
                with st.expander(f"🚛 Camion {truck_id+1} ({len(truck_routes)} arrêts)"):
                    truck_routes.sort(key=lambda x: x['bin_order'])
                    
                    total_weight = sum(route['weight'] for route in truck_routes)
                    total_distance = sum(route.get('distance_to_next', 0) for route in truck_routes if route.get('distance_to_next'))
                    total_time = sum(route.get('time_to_next', 0) for route in truck_routes if route.get('time_to_next'))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Poids total", f"{total_weight:.1f} kg")
                    with col2:
                        st.metric("Distance", format_distance(total_distance))
                    with col3:
                        st.metric("Temps estimé", format_duration(total_time))
                    
                    # Route table
                    route_data = []
                    for route in truck_routes:
                        route_data.append({
                            'Ordre': route['bin_order'] + 1,
                            'Coordonnées': f"{route['latitude']:.4f}, {route['longitude']:.4f}",
                            'Poids': f"{route['weight']:.1f} kg",
                            'Distance suivante': f"{route.get('distance_to_next', 0)/1000:.2f} km" if route.get('distance_to_next') else "Fin",
                            'Temps suivant': f"{route.get('time_to_next', 0)/60:.1f} min" if route.get('time_to_next') else "Fin"
                        })
                    
                    st.dataframe(pd.DataFrame(route_data), use_container_width=True)
        else:
            st.info("Aucune route trouvée pour cette simulation")
    except Exception as e:
        st.error(f"Erreur lors de la visualisation: {e}")
else:
    st.info("Sélectionnez ou lancez une simulation pour voir la visualisation")

# Section 6: Actions sur les simulations
if hasattr(st.session_state, 'current_simulation') and st.session_state.current_simulation:
    st.header("🗑️ Actions")
    
    if st.button("❌ Supprimer la simulation sélectionnée"):
        try:
            resp = requests.delete(f"{backend_url}/simulations/{st.session_state.current_simulation}")
            if resp.status_code == 200:
                st.success("Simulation supprimée!")
                del st.session_state.current_simulation
                st.rerun()
            else:
                st.error("Erreur lors de la suppression")
        except Exception as e:
            st.error(f"Erreur: {e}")
