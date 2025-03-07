from fastapi import FastAPI
from app.api.v1.endpoints import users  # Importamos el router de usuarios
from app.db import models  # No necesitamos `database` ni `engine`
from app.db import crud, schemas

# Crear la aplicación FastAPI
app = FastAPI()

# Incluir las rutas de usuarios en la API con el prefijo '/users'
app.include_router(users.router, prefix="/users", tags=["users"])

# Ruta raíz de ejemplo
@app.get("/")
def read_root():
    return {"message": "Welcome to the User Management API!"}
