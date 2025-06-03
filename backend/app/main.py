from fastapi import FastAPI
from .database import engine, Base
from .routers import bins

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trashway API")

app.include_router(bins.router)
