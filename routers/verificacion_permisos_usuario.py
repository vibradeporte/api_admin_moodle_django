import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *
from jwt_manager import JWTBearer

# Definir la longitud máxima del ID del cliente
max_length_id_cliente = 11 

# Cargar las variables de entorno desde un archivo .env
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

# Crear un enrutador de FastAPI para gestionar las rutas relacionadas con la verificación de permisos
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
        - ID_PERMISO -> Id del caso de uso al que tiene permisos ese usuario.
    """
    with engine.connect() as connection:
        # Definir la consulta SQL para obtener los permisos del usuario
        consulta_sql = text("""
            SELECT PU.`FID_CASO_USO-CLIENTE` AS ID_PERMISO
            FROM USUARIO U
            JOIN `CASO_USO-USUARIO` PU ON U.ID_USUARIO = PU.FID_USUARIO
            WHERE U.ID_USUARIO = :ID_USUARIO;
        """).params(ID_USUARIO=ID_USUARIO)
        
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
            # Si no hay resultados, retornar un error de permisos
            codigo = SIN_PERMISOS
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)


@verificacion_permisos_usuario_router.get("/verificacion_permisos_cliente", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_permisos_cliente(ID_CLIENTE: int):
    """
    ## **Descripción:**
        Servicio para validar los casos de uso contratados por un cliente junto con las fechas de contratación.

    ## **Parámetros obligatorios:**
        - ID_CLIENTE -> Corresponde al id del cliente en la base de datos.
       
    ## **Códigos retornados:**
        - 200 -> Retorna los datos del usuario.
        - 453 -> El usuario no tiene los permisos necesarios para acceder al caso de uso.

    ## **Campos retornados:**
        - ID_PERMISO -> Id del caso de uso al que tiene permisos ese cliente.
    """
    with engine.connect() as connection:
        # Definir la consulta SQL para obtener los permisos del usuario
        consulta_sql = text("""
            SELECT CU.NOMBRE_CORTO AS NOMBRE_CORTO, CC.`ID_CASO_USO-CLIENTE` AS ID_PERMISO
            FROM CLIENTE C
            JOIN `CASO_USO-CLIENTE` CC ON C.ID_CLIENTE = CC.FID_CLIENTE
            JOIN CASO_USO CU ON CU.ID_CASO_USO = CC.FID_CASO_USO
            WHERE (CC.FECHA_INCIO_CONTRATACION < CURDATE() AND CC.FECHA_FIN_CONTRATACION > CURDATE())
            AND C.ID_CLIENTE = :ID_CLIENTE;
        """).params(ID_CLIENTE=ID_CLIENTE)
        
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
            # Si no hay resultados, retornar un error de permisos
            codigo = SIN_PERMISOS
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)