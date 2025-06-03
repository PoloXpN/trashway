from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Bin(Base):
    __tablename__ = "bins"
    id = Column(Integer, primary_key=True, index=True)
    bin_id = Column(String, index=True)
    weight = Column(Float)
    presence = Column(Integer)
    timestamp = Column(String)
    street_number = Column(String)
    street_name = Column(String)
    postal_code = Column(String)
    city = Column(String)
    country = Column(String)
