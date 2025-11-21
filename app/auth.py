# app/auth.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import database, models, schemas

# ============================================================
# ⚙️ CONFIGURACIÓN GENERAL DE AUTENTICACIÓN
# ============================================================

SECRET_KEY = "clave_secreta_para_proyecto_local"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Esquema de autenticación (Bearer Token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Límite de bcrypt: 72 bytes
BCRYPT_MAX_LENGTH = 72


# ============================================================
# 🧩 FUNCIONES DE SEGURIDAD Y HASHING
# ============================================================

def get_password_hash(password: str) -> str:
    """
    Convierte una contraseña en un hash seguro usando bcrypt directamente.
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    
    # Convertir a bytes
    password_bytes = password.encode('utf-8')
    
    # Truncar si es muy larga
    if len(password_bytes) > BCRYPT_MAX_LENGTH:
        password_bytes = password_bytes[:BCRYPT_MAX_LENGTH]
    
    # Generar salt y hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Devolver como string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña coincida con su hash.
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        # Convertir a bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Truncar si es muy larga
        if len(password_bytes) > BCRYPT_MAX_LENGTH:
            password_bytes = password_bytes[:BCRYPT_MAX_LENGTH]
        
        # Verificar
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ============================================================
# 🧩 FUNCIONES PARA TOKENS JWT
# ============================================================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Genera un token JWT firmado con los datos del usuario."""
    to_encode = data.copy()

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    """Obtiene el usuario actual a partir del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


# ============================================================
# 🧩 FUNCIONES AUXILIARES DE AUTENTICACIÓN
# ============================================================

def authenticate_user(username: str, password: str, db: Session):
    """
    Verifica si el usuario existe y su contraseña es correcta.
    Devuelve el usuario si es válido, o False si no.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
    