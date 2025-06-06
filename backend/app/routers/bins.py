from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Bin
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BinCreate(BaseModel):
    bin_id: str
    weight: float
    presence: int
    longitude: float
    latitude: float

class BinUpdate(BaseModel):
    presence: int

class BinWeightUpdate(BaseModel):
    weight: float

class BinGeneralUpdate(BaseModel):
    weight: float = None
    presence: int = None

@router.post("/bins/", response_model=dict)
def create_bin(bin: BinCreate, db: Session = Depends(get_db)):
    bin_data = {
        "bin_id": bin.bin_id,
        "weight": bin.weight,
        "presence": bin.presence,
        "longitude": bin.longitude,
        "latitude": bin.latitude
    }
    db_bin = Bin(**bin_data)
    db.add(db_bin)
    db.commit()
    db.refresh(db_bin)
    return {"id": db_bin.id}

@router.get("/bins/", response_model=List[dict])
def read_bins(db: Session = Depends(get_db)):
    bins = db.query(Bin).all()
    result = []
    for b in bins:
        bin_dict = {
            "id": b.id,
            "bin_id": b.bin_id,
            "weight": b.weight,
            "presence": b.presence,
            "longitude": b.longitude,
            "latitude": b.latitude
        }
        result.append(bin_dict)
    return result

@router.delete("/bins/{bin_id}", response_model=dict)
def delete_bin(bin_id: int, db: Session = Depends(get_db)):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    db.delete(bin)
    db.commit()
    return {"success": True}

@router.patch("/bins/{bin_id}/presence", response_model=dict)
def update_bin_presence(bin_id: int, bin_update: BinUpdate, db: Session = Depends(get_db)):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    bin.presence = bin_update.presence
    db.commit()
    
    return {"success": True}

@router.patch("/bins/{bin_id}/weight", response_model=dict)
def update_bin_weight(bin_id: int, bin_weight_update: BinWeightUpdate, db: Session = Depends(get_db)):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    bin.weight = bin_weight_update.weight
    db.commit()
    
    return {"success": True}

@router.patch("/bins/{bin_id}", response_model=dict)
def update_bin_general(bin_id: int, bin_general_update: BinGeneralUpdate, db: Session = Depends(get_db)):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    if bin_general_update.presence is not None:
        bin.presence = bin_general_update.presence
    if bin_general_update.weight is not None:
        bin.weight = bin_general_update.weight
    db.commit()
    
    return {"success": True}
