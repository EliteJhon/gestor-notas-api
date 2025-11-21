# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.routes import users, notes
import os

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Gestor de Notas API")

# CORS - Configuración para producción
is_production = os.getenv("RENDER", False)
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "")

if is_production:
    # En producción: permite tu dominio de Render y otros que necesites
    origins = [
        RENDER_URL,  # Tu URL de Render
        "https://gestor-notas-api-1h1e.onrender.com",  # Si tienes frontend separado
    ]
    # Filtrar valores vacíos
    origins = [origin for origin in origins if origin]
    
    # Si no hay URLs específicas, usar lista vacía (más seguro)
    if not origins:
        origins = ["*"]
        allow_credentials = False
    else:
        allow_credentials = True
else:
    # En desarrollo local
    origins = [
        "http://localhost",
        "http://localhost:5500",
        "http://127.0.0.1",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
    ]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend
app.mount("/static", StaticFiles(directory="app/frontend"), name="static")

# Registrar routers
app.include_router(users.router)
app.include_router(notes.router)