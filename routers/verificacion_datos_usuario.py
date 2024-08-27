import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *  # Importa códigos de retorno personalizados
from jwt_manager import JWTBearer  # Importa el manejador de JWT para la autenticación

# Definir la longitud máxima del ID del cliente
max_length_id_cliente = 11 

# Cargar variables de entorno desde un archivo .env
load_dotenv()
usuario = os.getenv("USER_DB_UL")  # Usuario para la base de datos
contrasena = os.getenv("PASS_DB_UL")  # Contraseña para la base de datos
host = os.getenv("HOST_DB_UL")  # Host de la base de datos
nombre_base_datos = os.getenv("NAME_DB_UL")  # Nombre de la base de datos

# Codificar la contraseña para usar en la URL de conexión
contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
# Crear el motor de conexión a la base de datos
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crear un enrutador de FastAPI para gestionar la ruta de verificación de datos del usuario
verificacion_datos_usuario_router = APIRouter()

@verificacion_datos_usuario_router.get("/verificacion_datos_usuario", tags=['admin_moodle'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_datos_usuario(IDENTIFICACION: int):
    """
    ## **Descripción:**
        Servicio para validar la existencia del número de identificación en la base de datos.

    ## **Parámetros obligatorios:**
        - IDENTIFICACION -> Corresponde al número de cédula del usuario.
        
    ## **Códigos retornados:**
        - 200 -> Retorna los datos del usuario.
        - 452 -> No se encontró información sobre el número de identificación ingresado.

    ## **Campos retornados:**
        - ID_USUARIO -> Id del usuario.
        - NOMBRE -> Nombre del usuario.
        - APELLIDO -> Apellido del usuario.
        - MOVIL -> Número de celular del usuario.
        - CORREO -> Correo electrónico del usuario.
    """
    # Conectar a la base de datos
    with engine.connect() as connection:
        # Definir la consulta SQL para obtener los datos del usuario según la identificación
        consulta_sql = text("""
            SELECT u.ID_USUARIO, u.NOMBRE, u.APELLIDO, u.MOVIL, u.CORREO
            FROM USUARIO u
            WHERE u.IDENTIFICACION = :IDENTIFICACION;
        """).params(IDENTIFICACION=IDENTIFICACION)
        
        # Ejecutar la consulta y obtener los resultados
        result = connection.execute(consulta_sql)
        rows = result.fetchall()  # Obtener todas las filas del resultado
        column_names = result.keys()  # Obtener los nombres de las columnas

        # Convertir los resultados en una lista de diccionarios
        result_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            result_dicts.append(row_dict)

        # Verificar si se obtuvieron resultados y devolverlos
        if result_dicts:
            return JSONResponse(content=result_dicts)
        else:
            # Si no hay resultados, retornar un error de información no encontrada
            codigo = SIN_INFORMACION
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)
