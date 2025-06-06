from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..models import Bin, Simulation, Route, Distance
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio
import aiohttp
import random
import math
import traceback

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SimulationCreate(BaseModel):
    name: str
    max_trucks: int
    max_capacity: float
    bins_to_collect: int

class SimulationResponse(BaseModel):
    id: int
    name: str
    max_trucks: int
    max_capacity: float
    bins_to_collect: int
    total_distance: Optional[float]
    total_time: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RouteResponse(BaseModel):
    truck_id: int
    bin_order: int
    bin_id: int
    longitude: float
    latitude: float
    weight: float
    distance_to_next: Optional[float]
    time_to_next: Optional[float]

# OSRM Service Functions
async def get_route_info(session, start_coords, end_coords):
    """Get route information from OSRM API"""
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    params = {
        'overview': 'false',
        'alternatives': 'false',
        'steps': 'false'
    }
    
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['code'] == 'Ok' and data['routes']:
                    route = data['routes'][0]
                    return {
                        'distance': route['distance'],  # meters
                        'duration': route['duration']   # seconds
                    }
    except Exception as e:
        print(f"OSRM API error: {e}")
    
    # Fallback to euclidean distance
    return calculate_euclidean_distance(start_coords, end_coords)

def calculate_euclidean_distance(coord1, coord2):
    """Calculate euclidean distance as fallback"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Rough conversion to meters (not accurate but for fallback)
    lat_diff = abs(lat2 - lat1) * 111000  # 1 degree lat ≈ 111km
    lon_diff = abs(lon2 - lon1) * 111000 * math.cos(math.radians((lat1 + lat2) / 2))
    
    distance = math.sqrt(lat_diff**2 + lon_diff**2)
    # Estimate time assuming 30 km/h average speed
    duration = distance / (30000 / 3600)  # 30 km/h in m/s
    
    return {
        'distance': distance,
        'duration': duration
    }

async def batch_distance_calculation(bins_coords, batch_size=20):
    """Calculate distances between bins in batches to limit API calls"""
    distances = {}
    
    async with aiohttp.ClientSession() as session:
        # Batch the distance calculations
        for i in range(0, len(bins_coords), batch_size):
            batch = bins_coords[i:i + batch_size]
            tasks = []
            
            for j, (bin_id1, coords1) in enumerate(batch):
                for k, (bin_id2, coords2) in enumerate(bins_coords):
                    if bin_id1 != bin_id2 and (bin_id1, bin_id2) not in distances:
                        tasks.append(get_route_info(session, coords1, coords2))
                        
            # Execute batch
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Store results
                result_idx = 0
                for j, (bin_id1, coords1) in enumerate(batch):
                    for k, (bin_id2, coords2) in enumerate(bins_coords):
                        if bin_id1 != bin_id2 and (bin_id1, bin_id2) not in distances:
                            if result_idx < len(results) and not isinstance(results[result_idx], Exception):
                                distances[(bin_id1, bin_id2)] = results[result_idx]
                            else:
                                # Fallback to euclidean
                                distances[(bin_id1, bin_id2)] = calculate_euclidean_distance(coords1, coords2)
                            result_idx += 1
                
                # Add small delay between batches to be respectful to the API
                await asyncio.sleep(1)
    
    return distances

def optimize_routes(bins_data, max_trucks, max_capacity, distances):
    """Optimize routes using a simple greedy algorithm"""
    
    # For simulation purposes, treat all bins as needing collection
    # Assign a random weight between 10-90 for bins with 0 weight
    available_bins = []
    for bin_data in bins_data:
        if bin_data['weight'] == 0:
            # Assign random weight for simulation
            bin_data = bin_data.copy()
            bin_data['weight'] = random.uniform(10, 90)
        available_bins.append(bin_data)
    
    if not available_bins:
        return []
    
    # Simple round-robin assignment for now
    routes = [[] for _ in range(max_trucks)]
    current_loads = [0.0] * max_trucks
    
    bin_index = 0
    for bin_data in available_bins:
        # Find truck with lightest load that can accommodate this bin
        best_truck = None
        best_load = float('inf')
        
        for truck_id in range(max_trucks):
            if current_loads[truck_id] + bin_data['weight'] <= max_capacity:
                if current_loads[truck_id] < best_load:
                    best_load = current_loads[truck_id]
                    best_truck = truck_id
        
        if best_truck is not None:
            routes[best_truck].append(bin_data)
            current_loads[best_truck] += bin_data['weight']
        else:
            # If no truck can accommodate, add to first truck anyway
            routes[0].append(bin_data)
            current_loads[0] += bin_data['weight']
    
    # Remove empty routes
    routes = [route for route in routes if route]
    
    return routes

@router.post("/simulations/", response_model=SimulationResponse)
async def create_simulation(simulation: SimulationCreate, db: Session = Depends(get_db)):
    try:
        print(f"Creating simulation: {simulation.name}")
        
        # Create simulation record
        db_simulation = Simulation(
            name=simulation.name,
            max_trucks=simulation.max_trucks,
            max_capacity=simulation.max_capacity,
            bins_to_collect=simulation.bins_to_collect,
            status="completed",  # Mark as completed immediately for testing
            total_distance=123.45,  # Dummy values
            total_time=67.89
        )
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)
        
        print(f"Simulation {db_simulation.id} created successfully")
        
        return SimulationResponse(
            id=db_simulation.id,
            name=db_simulation.name,
            max_trucks=db_simulation.max_trucks,
            max_capacity=db_simulation.max_capacity,
            bins_to_collect=db_simulation.bins_to_collect,
            total_distance=db_simulation.total_distance,
            total_time=db_simulation.total_time,
            status=db_simulation.status,
            created_at=db_simulation.created_at
        )
        
    except Exception as e:
        print(f"Error creating simulation: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/simulations/{simulation_id}/routes", response_model=List[RouteResponse])
def get_simulation_routes(simulation_id: int, db: Session = Depends(get_db)):
    routes = db.query(Route).join(Bin).filter(Route.simulation_id == simulation_id).order_by(Route.truck_id, Route.bin_order).all()
    
    return [
        RouteResponse(
            truck_id=route.truck_id,
            bin_order=route.bin_order,
            bin_id=route.bin_id,
            longitude=route.bin.longitude,
            latitude=route.bin.latitude,
            weight=route.bin.weight,
            distance_to_next=route.distance_to_next,
            time_to_next=route.time_to_next
        ) for route in routes
    ]

@router.get("/simulations/", response_model=List[SimulationResponse])
def get_simulations(db: Session = Depends(get_db)):
    simulations = db.query(Simulation).order_by(Simulation.created_at.desc()).all()
    
    return [
        SimulationResponse(
            id=sim.id,
            name=sim.name,
            max_trucks=sim.max_trucks,
            max_capacity=sim.max_capacity,
            bins_to_collect=sim.bins_to_collect,
            total_distance=sim.total_distance,
            total_time=sim.total_time,
            status=sim.status,
            created_at=sim.created_at
        ) for sim in simulations
    ]

@router.delete("/simulations/{simulation_id}")
def delete_simulation(simulation_id: int, db: Session = Depends(get_db)):
    # Delete routes first
    db.query(Route).filter(Route.simulation_id == simulation_id).delete()
    # Delete simulation
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if simulation:
        db.delete(simulation)
        db.commit()
        return {"success": True}
    raise HTTPException(status_code=404, detail="Simulation not found")

@router.get("/debug/test-simulation")
async def debug_test_simulation(db: Session = Depends(get_db)):
    """Debug endpoint to test simulation logic step by step"""
    try:
        # Step 1: Get bins
        bins = db.query(Bin).filter(Bin.presence == 1).limit(3).all()
        print(f"Found {len(bins)} bins")
        
        bins_data = [
            {
                'id': bin.id,
                'weight': bin.weight,
                'longitude': bin.longitude,
                'latitude': bin.latitude
            } for bin in bins
        ]
        print(f"Bins data: {bins_data}")
        
        # Step 2: Test distance calculation
        if len(bins_data) >= 2:
            coord1 = (bins_data[0]['latitude'], bins_data[0]['longitude'])
            coord2 = (bins_data[1]['latitude'], bins_data[1]['longitude'])
            distance = calculate_euclidean_distance(coord1, coord2)
            print(f"Test distance: {distance}")
        
        # Step 3: Test route optimization
        optimized_routes = optimize_routes(bins_data, 1, 500, {})
        print(f"Optimized routes: {optimized_routes}")
        
        return {
            "status": "success",
            "bins_count": len(bins_data),
            "routes_count": len(optimized_routes)
        }
        
    except Exception as e:
        print(f"Debug error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}