# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# -------------------------------------------------------------
# MODELO DE USUARIO
# -------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)  # 👈 ESTE campo debe existir
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(String)  # admin o empleado
    subrol = Column(String, nullable=True)  # jefe, supervisor, cajero, contador, etc.

    activo = Column(Boolean, default=True)              # Si el usuario está activo o no
    creado_en = Column(DateTime, default=datetime.utcnow)  # Fecha de creación

    # Relación con las notas
    notas_creadas = relationship("Note", back_populates="creador", foreign_keys="Note.creador_id")
    notas_asignadas = relationship("Note", back_populates="destinatario", foreign_keys="Note.destinatario_id")

# -------------------------------------------------------------
# MODELO DE NOTA
# -------------------------------------------------------------
class Note(Base):
    __tablename__ = "notes"  # Nombre de la tabla

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    contenido = Column(Text, nullable=False)

    estado = Column(String, default="pendiente")  # pendiente, en_progreso, completado

    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con el creador (quien creó la nota)
    creador_id = Column(Integer, ForeignKey("users.id"))
    # Relación con el destinatario (quien debe completarla)
    destinatario_id = Column(Integer, ForeignKey("users.id"))

    # Relaciones bidireccionales (para acceder fácilmente desde ambos lados)
    creador = relationship("User", foreign_keys=[creador_id], back_populates="notas_creadas")
    destinatario = relationship("User", foreign_keys=[destinatario_id], back_populates="notas_asignadas")
