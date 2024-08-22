import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *
from jwt_manager import JWTBearer

max_length_id_cliente = 11 

# Cargar variables de entorno
load_dotenv()
usuario = os.getenv("USER_DB_UL")
contrasena = os.getenv("PASS_DB_UL")
host = os.getenv("HOST_DB_UL")
nombre_base_datos = os.getenv("NAME_DB_UL")

# Codificar la contraseña para la URL de conexión
contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crear el enrutador de FastAPI
verificacion_datos_usuario_router = APIRouter()


@verificacion_datos_usuario_router.get("/verificacion_datos_usuario", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_datos_usuario(IDENTIFICACION: int):
    """
    ## **Descripción:**
        Servicio para validar la existencia del número de identificación en la base de datos.

    ## **Parámetros obligatorios:**
        - IDENTIFICACION -> Corresponde al número de cedula del usuario.
        
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
    with engine.connect() as connection:
        consulta_sql = text("""
            SELECT u.ID_USUARIO, u.NOMBRE, u.APELLIDO, u.MOVIL, u.CORREO FROM USUARIO u WHERE u.IDENTIFICACION = :IDENTIFICACION;
        """).params(IDENTIFICACION=IDENTIFICACION)
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            result_dicts.append(row_dict)

        if result_dicts:
            return JSONResponse(content=result_dicts)
        else:
            codigo = SIN_INFORMACION
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)
