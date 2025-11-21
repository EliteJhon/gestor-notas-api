# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ============================================================
# 🔑 USUARIOS
# ============================================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    rol: str = "cliente"  # Valor por defecto
    subrol: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    rol: str
    subrol: Optional[str] = None

    class Config:
        from_attributes = True


# Alias para mantener compatibilidad
UserResponse = UserOut


# ============================================================
# 📝 NOTAS
# ============================================================

class NoteCreate(BaseModel):
    titulo: str
    contenido: str
    estado: Optional[str] = "pendiente"
    destinatario_id: Optional[int] = None  # 👈 AGREGAR ESTE CAMPO


class NoteOut(BaseModel):
    id: int
    titulo: str
    contenido: str
    estado: str
    creado_en: datetime
    actualizado_en: datetime
    creador_id: Optional[int] = None
    destinatario_id: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================================
# 🔐 TOKENS
# ============================================================

class TokenData(BaseModel):
    username: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut  # 👈 AGREGAR USUARIO EN LA RESPUESTA


# ============================================================
# 🔄 RESPUESTAS COMPLEJAS
# ============================================================

class NoteForUser(BaseModel):
    id: int
    titulo: str
    contenido: str
    estado: str

    class Config:
        from_attributes = True


class UserWithNotes(BaseModel):
    id: int
    username: str
    email: EmailStr
    rol: str
    notes: List[NoteForUser] = []

    class Config:
        from_attributes = True