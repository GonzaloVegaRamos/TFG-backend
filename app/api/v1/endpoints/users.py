from fastapi import APIRouter, Depends, HTTPException, status
from app.db import crud, schemas

# Crear el router de usuarios
router = APIRouter()

# Ruta para registrar un nuevo usuario
@router.post("/register", response_model=schemas.UserCreate)
async def register_user(
    user: schemas.UserCreate
):
    # Comprobamos si el usuario ya existe por email
    existing_user = crud.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado",
        )
    
    # Crear el nuevo usuario en la base de datos
    new_user = crud.create_user(user)
    return new_user  # Retorna el usuario recién creado

# Ruta para obtener un usuario por email
@router.get("/{email}", response_model=schemas.UserCreate)
async def get_user_by_email(
    email: str
):
    # Buscar el usuario en la base de datos
    user = crud.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrada",
        )
    return user  # Retorna el usuario encontrado
