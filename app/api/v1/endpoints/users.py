import re
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import authenticate_token  # Importar funciones de auth
from app.db.database import get_supabase_client  # Usar el cliente de Supabase para interactuar con la DB
from passlib.context import CryptContext
from app.db import schemas  # Tus esquemas de Pydantic
from fastapi import Header
from uuid import UUID, uuid4
from fastapi import Header, HTTPException
from uuid import UUID, uuid4
from fastapi import Header, HTTPException
from supabase import Client
from uuid import UUID, uuid4

# Crear el router de usuarios
router = APIRouter()

# Instanciamos el contexto de passlib para verificar las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Obtener cliente de Supabase
supabase = get_supabase_client()

# Función para validar el formato del email
def is_valid_email(email: str) -> bool:
    # Expresión regular para validar el formato de correo electrónico
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))


@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate):
    # Validar el formato del email
    if not is_valid_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del correo electrónico no es válido"
        )
    
    # Verificar si ya existe en Auth
    try:
        existing_user = supabase.auth.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo electrónico ya está registrado",
            )
    except Exception:
        pass

    # Validar campos obligatorios
    if not user.password or not user.username or not user.edad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todos los campos son requeridos: username, password, y edad"
        )

    # Crear usuario en Supabase Auth
    try:
        new_user = supabase.auth.sign_up({
            'email': user.email,
            'password': user.password
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el usuario: {str(e)}"
        )

    # Crear usuario en la tabla personalizada (users o profiles)
    try:
        # Aquí insertamos el nuevo usuario en la tabla 'users'
        supabase.table("users").insert({
            "auth_id": new_user.user.id,  # UUID de Supabase Auth
            "email": user.email,
            "username": user.username,
            "gender": user.gender,
            "style_preference": user.style_preference,
            "edad": user.edad
        }).execute()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario en tabla users: {str(e)}"
        )

    # Respuesta final, no necesitamos detalles adicionales
    return schemas.UserResponse(
        id=new_user.user.id,
        email=user.email,
        username=user.username,
        gender=user.gender,
        style_preference=user.style_preference,
        edad=user.edad
    )


@router.get("/user/{user_id}", response_model=schemas.UserResponse)
async def get_user_by_id(user_id: str):
    try:
        # Usamos supabase para obtener el usuario por su ID
        user = supabase.auth.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Si el usuario existe, retornamos la información del usuario
        return schemas.UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            gender=user.gender,
            style_preference=user.style_preference,
            edad=user.edad
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener el usuario: {str(e)}"
        )


@router.post("/login")
async def login_user(user: schemas.UserLogin):
    try:
        db_user = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        if not db_user or "error" in db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        token = db_user.session.access_token
        return {"access_token": token, "token_type": "bearer"}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales incorrectas"
        )


@router.get("/me")
async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    # Extraer el token de la cabecera Authorization
    token = authorization.split("Bearer ")[1]

    try:
        # Usar Supabase para obtener la información del usuario con el token
        user_info = supabase.auth.get_user(token)  # Validar el token con Supabase
        
        if not user_info or not user_info.user:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Obtener el auth_id
        auth_id = user_info.user.id

        # Retornar solo el auth_id
        return {
            "auth_id": auth_id
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")


@router.get("/users", response_model=list[schemas.UserResponse])
async def get_all_users():
    try:
        # Aquí asumo que tienes una tabla 'profiles' en tu base de datos de Supabase
        response = supabase.table("profiles").select("*").execute()
        
        if response.error:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener los usuarios: {response.error.message}"
            )
        
        users = response.data
        return [
            schemas.UserResponse(
                id=user.get("id"),
                email=user.get("email"),
                username=user.get("username"),
                gender=user.get("gender"),
                style_preference=user.get("style_preference"),
                edad=user.get("edad")
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )


@router.get("/ropa")
async def get_ropa(tipo: str = None):
    """Obtener las prendas de ropa filtradas por tipo"""
    try:
        if tipo:
            # Si el parámetro 'tipo' está presente, filtramos las prendas por ese tipo
            response = supabase.table("ropa").select("*").eq("tipo", tipo).execute()
        else:
            # Si no se pasa el parámetro 'tipo', obtenemos todas las prendas de ropa
            response = supabase.table("ropa").select("*").execute()

        # Verificamos si la respuesta es exitosa
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron prendas de ropa."
            )

        # Devolvemos las prendas de ropa obtenidas
        return response.data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al obtener las prendas de ropa: {str(e)}"
        )



from uuid import UUID
from fastapi import HTTPException, Header
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from fastapi import HTTPException

@router.post("/conjuntos")
async def guardar_conjunto(conjunto: schemas.ConjuntoCreate, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    token = authorization.split("Bearer ")[1]

    try:
        # Validación de usuario (tu código actual)
        user_info = supabase.auth.get_user(token)
        if not user_info or not user_info.user:
            raise HTTPException(status_code=401, detail="Token inválido")

        user_data_response = supabase.table("users").select("id").eq("auth_id", user_info.user.id).single().execute()
        user_data = user_data_response.data

        # Preparar datos para Supabase
        datos_conjunto = {
            "nombre": conjunto.nombre,
            "usuario": user_data["id"],
            # Conversión explícita a string para Supabase
            "camiseta": str(conjunto.camiseta) if conjunto.camiseta else None,
            "ral": str(conjunto.ral) if conjunto.ral else None,
            "pb": str(conjunto.pb) if conjunto.pb else None,
            "calzado": str(conjunto.calzado) if conjunto.calzado else None,
            "accesorio": str(conjunto.accesorio) if conjunto.accesorio else None,
            "chaqueta": str(conjunto.chaqueta) if conjunto.chaqueta else None,
        }

        # Insertar en Supabase
        respuesta = supabase.table("conjuntos").insert(datos_conjunto).execute()

        if not respuesta.data:
            raise HTTPException(status_code=500, detail="Error al guardar el conjunto")

        return {
            "mensaje": "Conjunto guardado exitosamente",
            "conjunto": respuesta.data[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")