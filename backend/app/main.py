from fastapi import FastAPI
from .database import engine, Base
from .routers import bins, simulations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trashway API")

app.include_router(bins.router)
app.include_router(simulations.router)
