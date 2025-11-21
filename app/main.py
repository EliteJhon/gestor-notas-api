# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.routes import users, notes

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gestor de Notas API")

# CORS
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend
app.mount("/static", StaticFiles(directory="app/frontend"), name="static")

# Registrar routers
app.include_router(users.router)  # prefix="/auth"
app.include_router(notes.router)  # prefix="/notes" 