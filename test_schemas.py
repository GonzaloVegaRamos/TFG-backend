from app.db.schemas import UserCreate

from pydantic import ValidationError

def test_valid_data():
    # Datos válidos para crear un usuario
    valid_data = {
        "email": "user@example.com",
        "password": "securepassword123",
        "username": "testuser",
        "gender": "male",  # Opcional
        "style_preference": "casual",  # Opcional
        "edad": 25
    }

    # Intentamos crear un objeto de tipo UserCreate con los datos válidos
    try:
        user = UserCreate(**valid_data)
        print(f"User created successfully: {user}")
    except ValidationError as e:
        print(f"Validation error: {e}")

def test_invalid_data():
    # Datos inválidos para crear un usuario (por ejemplo, email mal formado)
    invalid_data = {
        "email": "user@example.com",  # Email inválido
        "password": "securepassword123",
        "username": "testuser",
        "gender": "male",
        "style_preference": "casual",
        "edad": 25
    }

    # Intentamos crear un objeto de tipo UserCreate con los datos inválidos
    try:
        user = UserCreate(**invalid_data)
        print(f"User created successfully: {user}")
    except ValidationError as e:
        print(f"Validation error: {e}")

# Ejecutar las pruebas
test_valid_data()
test_invalid_data()
