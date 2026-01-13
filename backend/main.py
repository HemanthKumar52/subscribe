import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import purchase, auth, rtdn
from . import models
from .database import engine

# Create tables (simple migration)
models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Subscribo Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(purchase.router)
app.include_router(auth.router)
app.include_router(rtdn.router)


@app.get("/")
def read_root():
    return {"message": "Subscribo API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
