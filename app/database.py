from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------------------
# 1️⃣ URL de conexión a la base de datos
# -------------------------------------------------------------
# "sqlite:///./gestor_notas.db" significa:
# - Usar SQLite como motor
# - Guardar la base de datos en el archivo "gestor_notas.db" (en el mismo directorio)

SQLALCHEMY_DATABASE_URL = "sqlite:///./gestor_notas.db"

# -------------------------------------------------------------
# 2️⃣ Creación del "motor" de base de datos
# -------------------------------------------------------------
# El engine es el objeto que conecta SQLAlchemy con la base de datos.
# 'connect_args' es obligatorio para SQLite cuando se usa en archivos locales.

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# -------------------------------------------------------------
# 3️⃣ Creación de la "sesión"
# -------------------------------------------------------------
# La sesión es la que se usa en las operaciones con la BD (agregar, leer, modificar, borrar).
# autocommit=False -> para controlar cuándo guardar
# autoflush=False -> no sincroniza automáticamente los cambios

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------------------------------------------
# 4️⃣ Base para los modelos
# -------------------------------------------------------------
# Aquí se define una clase base de la que heredarán todos los modelos
# (por ejemplo, User, Note, etc).

Base = declarative_base()


# -------------------------------------------------------------
# 5️⃣ Función auxiliar para obtener sesión
# -------------------------------------------------------------
# FastAPI usa dependencias para abrir y cerrar la conexión con la base.
# Esta función devolverá una sesión a cada endpoint que lo necesite.

def get_db():
    db = SessionLocal()
    try:
        yield db  # Se entrega la conexión
    finally:
        db.close()  # Se cierra cuando termina
