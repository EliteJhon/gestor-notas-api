# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from app import database, models, schemas, auth
from app.auth import get_password_hash

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"]
)

@router.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Validar rol
    if user.rol not in ["administrador", "cliente"]:
        raise HTTPException(
            status_code=400,
            detail="El rol debe ser 'administrador' o 'cliente'"
        )
    
    # Verificar usuario o correo duplicado
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) |
        (models.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El usuario o correo ya existen"
        )

    # Encriptar contraseña
    hashed_password = get_password_hash(user.password)

    # Crear nuevo usuario
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        rol=user.rol,
        subrol=user.subrol
    )

    # Guardar en DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=schemas.TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """
    Autenticación del usuario.
    Devuelve token JWT válido si las credenciales son correctas.
    """
    user = auth.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    # Crear token JWT
    access_token = auth.create_access_token(
        data={"sub": user.username}
    )

    # Convertir usuario a schema
    user_out = schemas.UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        rol=user.rol,
        subrol=user.subrol
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_out
    }


@router.get("/me", response_model=schemas.UserOut)
def get_current_profile(
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Devuelve la información del usuario autenticado.
    """
    return current_user


# 🔧 FIXED: Función auxiliar para validar y corregir emails
def validate_email(email: str) -> str:
    """
    Valida y corrige emails inválidos.
    Si el email no tiene @, lo convierte a un formato válido.
    """
    if not email:
        return "sin-email@ejemplo.com"
    
    # Si ya tiene @, devolverlo tal cual
    if "@" in email:
        return email
    
    # Si no tiene @, agregarlo (asumiendo que es un username)
    # Ejemplo: "usuario" -> "usuario@ejemplo.com"
    return f"{email}@ejemplo.com"


@router.get("/users", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Devuelve lista de usuarios solo si el usuario autenticado es administrador.
    Corrige emails inválidos antes de devolverlos.
    """
    if current_user.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver la lista de usuarios"
        )

    users = db.query(models.User).all()
    
    # Convertir usuarios a schemas, validando emails
    result = []
    for user in users:
        try:
            # Intentar crear el schema con el email original
            user_out = schemas.UserOut(
                id=user.id,
                username=user.username,
                email=user.email,
                rol=user.rol,
                subrol=user.subrol
            )
            result.append(user_out)
        except Exception as e:
            # Si falla la validación del email, corregirlo
            print(f"Email inválido para usuario {user.id} ({user.username}): {user.email}")
            corrected_email = validate_email(user.email)
            user_out = schemas.UserOut(
                id=user.id,
                username=user.username,
                email=corrected_email,
                rol=user.rol,
                subrol=user.subrol
            )
            result.append(user_out)
    
    return result