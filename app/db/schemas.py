from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr  # Validación para un email correcto
    password: str    # La contraseña en texto, que luego en el backend será encriptada
    username: str    # Nombre de usuario
    gender: Optional[str] = None  # Campo opcional para el género
    style_preference: Optional[str] = None  # Preferencia de estilo opcional
    edad: int        # Edad como un número entero

    class Config:
        # Esta configuración permite que se usen los nombres de las columnas de la BD (en minúsculas)
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    gender: Optional[str] = None
    style_preference: Optional[str] = None
    edad: int

    class Config:
        orm_mode = True
