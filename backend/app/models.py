from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Bin(Base):
    __tablename__ = "bins"
    id = Column(Integer, primary_key=True, index=True)
    bin_id = Column(String, index=True, unique=True)
    weight = Column(Float)
    presence = Column(Integer)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    max_trucks = Column(Integer, nullable=False)
    max_capacity = Column(Float, nullable=False)
    bins_to_collect = Column(Integer, nullable=False)
    total_distance = Column(Float)
    total_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    
    routes = relationship("Route", back_populates="simulation")

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    truck_id = Column(Integer, nullable=False)
    bin_order = Column(Integer, nullable=False)
    bin_id = Column(Integer, ForeignKey("bins.id"), nullable=False)
    distance_to_next = Column(Float)
    time_to_next = Column(Float)
    
    simulation = relationship("Simulation", back_populates="routes")
    bin = relationship("Bin")

class Distance(Base):
    __tablename__ = "distances"
    id = Column(Integer, primary_key=True, index=True)
    from_bin_id = Column(Integer, ForeignKey("bins.id"), nullable=False)
    to_bin_id = Column(Integer, ForeignKey("bins.id"), nullable=False)
    distance = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    
    from_bin = relationship("Bin", foreign_keys=[from_bin_id])
    to_bin = relationship("Bin", foreign_keys=[to_bin_id])