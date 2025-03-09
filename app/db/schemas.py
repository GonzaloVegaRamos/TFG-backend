from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str  # Ahora es solo un string, sin validación de correo electrónico
    password: str    # La contraseña en texto, que luego en el backend será encriptada
    username: str    # Nombre de usuario
    gender: Optional[str] = None  # Campo opcional para el género
    style_preference: Optional[str] = None  # Preferencia de estilo opcional
    edad: int        # Edad como un número entero

    class Config:
        # Esta configuración permite que se usen los nombres de las columnas de la BD (en minúsculas)
        orm_mode = True

class UserResponse(BaseModel):
    id: str 
    email: str  # Esto también lo cambiamos a str
    username: str
    gender: Optional[str] = None
    style_preference: Optional[str] = None
    edad: int

    class Config:
        orm_mode = True
