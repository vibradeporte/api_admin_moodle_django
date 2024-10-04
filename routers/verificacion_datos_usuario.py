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
engine = create_engine(DATABASE_URL)

# Crear el enrutador de FastAPI
verificacion_datos_usuario_router = APIRouter()


@verificacion_datos_usuario_router.get("/verificacion_datos_usuario", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_datos_usuario(IDENTIFICACION: int, IDENTIFICADOR_PAG_INICIO: str):
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
            SELECT
            c.URL_MOODLE as URL_MOODLE,
            c.TOKEN_MOODLE as TOKEN_MOODLE,
            c.PREFIJO_TABLAS as PREFIJO_TABLAS,
            c.MOTOR_BD as MOTOR_BD,
            c.SERVIDOR as SERVIDOR_BD,
            c.PUERTO as PUERTO_BD,
            c.USUARIO as USUARIO_BD,
            c.CONTRASENA as CONTRASENA_BD,
            c.NOMBRE_BD as NOMBRE_BD,
            c.CORREO_MATRICULA as CORREO_MATRICULA,
            c.CORREO_ENVIO_BIENVENIDAS as CORREO_ENVIO_BIENVENIDAS,
            c.CORREO_ADMIN_MOODLE as CORREO_ADMIN_MOODLE,
            u.ID_USUARIO as ID_USUARIO,
            u.NOMBRE as NOMBRE,
            u.APELLIDO as APELLIDO,
            u.MOVIL as MOVIL,
            u.CORREO as CORREO
        FROM
            USUARIO AS u
        JOIN CLIENTE AS c ON u.FID_CLIENTE = c.ID_CLIENTE
        JOIN PERSONALIZACION P ON P.FID_CLIENTE = c.ID_CLIENTE
        WHERE P.IDENTIFICADOR_PAG_INICIO = :IDENTIFICADOR_PAG_INICIO
        AND u.IDENTIFICACION = :IDENTIFICACION;
        """).params(IDENTIFICACION=IDENTIFICACION, IDENTIFICADOR_PAG_INICIO=IDENTIFICADOR_PAG_INICIO)
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
