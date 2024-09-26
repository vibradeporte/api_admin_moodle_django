import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends
from return_codes import *  # Importa códigos de retorno personalizados
from jwt_manager import JWTBearer  # Importa el manejador de JWT para la autenticación

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

# Crear un enrutador de FastAPI para gestionar la ruta de datos de personalización del cliente
datos_personalizacion_cliente_router = APIRouter()

@datos_personalizacion_cliente_router.get("/datos_personalizacion_cliente", tags=['admin_moodle'], status_code=200, dependencies=[Depends(JWTBearer())])
def datos_personalizacion_cliente(IDENTIFICADOR_PAG_INICIO: str):
    """
    ## **Descripción:**
        Servicio para retornar los datos de personalización del asistente de un cliente específico.

    ## **Parámetros obligatorios:**
        - IDENTIFICADOR_PAG_INICIO -> Corresponde al nombre del cliente en hash.
        
    ## **Códigos retornados:**
        - 200 -> Retorna los datos de personalización del cliente.
        
    ## **Campos retornados:**
        - ID_PERSONALIZACION -> Id principal en la tabla PERSONALIZACION.
        - FID_CLIENTE -> Foreign key del CLIENTE.
        - IDENTIFICADOR_PAG_INICIO -> Nombre del cliente en formato hash.
        - URL_IMAGEN_FONDO -> Url de la imagen de fondo que tendrá el asistente.
        - URL_LOGO -> Url de la imagen del logo del asistente.
        - POSICION_AUTENTICACION -> Posición de la autenticación. C:Centro, D:Derecha, I:Izquierda.
        - COLOR_BASE -> Color base de la página en formato hexadecimal.
        - TIPO_LETRA_TITULO -> Tipo de letra para los títulos del asistente.
        - TIPO_LETRA_TEXTOS -> Tipo de letra para los textos normales del asistente.
    """
    # Conectar a la base de datos
    with engine.connect() as connection:
        # Definir la consulta SQL para obtener los datos de personalización según el identificador
        consulta_sql = text("""
            SELECT * FROM PERSONALIZACION WHERE IDENTIFICADOR_PAG_INICIO = :IDENTIFICADOR_PAG_INICIO;
        """).params(IDENTIFICADOR_PAG_INICIO=IDENTIFICADOR_PAG_INICIO)
        
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
            # Si no hay resultados, retornar un error de registros no encontrados
            codigo = SIN_REGISTROS
            mensaje = HTTP_MESSAGES.get(codigo)
            raise HTTPException(codigo, mensaje)