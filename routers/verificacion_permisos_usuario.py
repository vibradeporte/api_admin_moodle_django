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
verificacion_permisos_usuario_router = APIRouter()

@verificacion_permisos_usuario_router.get("/verificacion_permisos_usuario", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_permisos_usuario(ID_USUARIO: int):
    """
    ## **Descripción:**
        Servicio para validar los permisos necesarios para la consulta del usuario en un caso de uso específico.

    ## **Parámetros obligatorios:**
        - ID_USUARIO -> Corresponde al número de cédula del usuario.
       
    ## **Códigos retornados:**
        - 200 -> Retorna los datos del usuario.
        - 453 -> El usuario no tiene los permisos necesarios para acceder al caso de uso.

    ## **Campos retornados:**
        - ID_USUARIO -> Id del usuario.
        - NOMBRE -> Nombre del usuario.
        - NOMBRE_PERMISO -> Nombre del permiso.
        - DESCRIPCION -> Descripción del permiso.
       
    """
    with engine.connect() as connection:
        consulta_sql = text("""
            
SELECT PU.FID_PERMISO AS ID_PERMISO FROM USUARIO U JOIN `PERMISO-USUARIO` PU ON U.ID_USUARIO = PU.FID_USUARIO JOIN PERMISO P ON PU.FID_PERMISO = P.ID_PERMISO WHERE U.ID_USUARIO = :ID_USUARIO;
        """).params(ID_USUARIO=ID_USUARIO)
        
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
            codigo = SIN_PERMISOS
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)
