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
    timestamp: str = None
    street_number: str = "1"
    street_name: str = "Rue de Paris"
    postal_code: str = "75000"
    city: str = "Paris"
    country: str = "France"

class BinUpdate(BaseModel):
    presence: int

@router.post("/bins/", response_model=dict)
def create_bin(bin: BinCreate, db: Session = Depends(get_db)):
    # Create a dictionary with required fields
    bin_data = {
        "bin_id": bin.bin_id,
        "weight": bin.weight,
        "presence": bin.presence,
        "timestamp": bin.timestamp or datetime.utcnow().isoformat()
    }
    
    # Add optional address fields if they exist in the model
    for field in ["street_number", "street_name", "postal_code", "city", "country"]:
        if hasattr(bin, field):
            bin_data[field] = getattr(bin, field)
    
    # Create the database object
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
            "timestamp": b.timestamp
        }
        
        # Handle optional address fields that might be missing in older records
        for field in ["street_number", "street_name", "postal_code", "city", "country"]:
            try:
                bin_dict[field] = getattr(b, field, "")
            except:
                bin_dict[field] = ""
                
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
