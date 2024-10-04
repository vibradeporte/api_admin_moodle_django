import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from return_codes import *  # Importa códigos de retorno personalizados
from jwt_manager import JWTBearer  # Importa el manejador de JWT para la autenticación
import numpy as np
import math
import json
from bs4 import BeautifulSoup
from utils.codigo_utils import *
from utils.conexion_utils import create_connection
from models.DBModels import ConexionBD
# Cargar variables de entorno desde un archivo .env
load_dotenv()
#usuario = os.getenv("USER_DB_RO")
#contrasena = os.getenv("PASS_DB_RO")
#host = os.getenv("HOST_DB_RO")
#nombre_base_datos = os.getenv("NAME_DB_RO")

# Codificar la contraseña para usar en la URL de conexión
#contrasena_codificada = quote_plus(contrasena)
#DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"

# Crear el motor de conexión a la base de datos
#engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crear un enrutador de FastAPI para gestionar las rutas de verificación de grupos
verificacion_grupos_router = APIRouter()

@verificacion_grupos_router.post("/verificacion_grupo_existe", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_grupo_existe(cadena_conexion: ConexionBD, GRUPO: str, COURSEID: int):
    """
    Verifica si un grupo con el nombre dado existe en Moodle.
    
    Parámetros:
        - GRUPO: Nombre del grupo.
        - COURSEID: ID del curso.

    Retorna:
        - Lista de grupos que coinciden con el nombre dado.
    """
    engine = create_connection(cadena_conexion)
    with engine.connect() as connection:
        consulta_sql = text("""
            SELECT DISTINCT g.id 
            FROM mdl_groups g 
            WHERE g.name = :GRUPO AND g.courseid = :COURSEID;
        """).params(GRUPO=GRUPO, COURSEID=COURSEID)
        
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = [dict(zip(column_names, row)) for row in rows]

        return JSONResponse(content=result_dicts)

@verificacion_grupos_router.post("/listado_grupos", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def listado_grupos(cadena_conexion: ConexionBD,COURSEID: int = None):
    """
    Obtiene el nombre de todos los grupos en Moodle.

    Parámetros:
        - COURSEID: ID del curso (opcional).

    Retorna:
        - Listado de grupos en Moodle.
        - Cada grupo incluye 'name' y 'summary'.
    """
    engine = create_connection(cadena_conexion)
    with engine.connect() as connection:
        consulta_sql = text("""
            SELECT DISTINCT g.name, g.description
            FROM mdl_groups g WHERE g.courseid = :COURSEID;
        """).params(COURSEID=COURSEID)
        
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            # Convertir el campo summary de HTML a texto plano
            if row_dict.get('description'):
                soup = BeautifulSoup(row_dict['description'], 'html.parser')
                row_dict['description'] = soup.get_text()
            result_dicts.append(row_dict)

        return JSONResponse(content=result_dicts)

class StringScoreCalculator:
    def __init__(self):
        self.bag = np.zeros((256, 256))

    def calculate_similarity_score(self, array1: str, array2: str) -> float:
        """Calcula el puntaje de similitud entre dos cadenas."""
        if not isinstance(array1, str) or not isinstance(array2, str):
            return 0.0

        byte_array1 = array1.encode('utf-8')
        byte_array2 = array2.encode('utf-8')

        return self._calculate_similarity_score(byte_array1, byte_array2)

    def _calculate_similarity_score(self, byte_array1: bytes, byte_array2: bytes) -> float:
        """Calcula el puntaje de similitud utilizando bigramas."""
        length1, length2 = len(byte_array1), len(byte_array2)
        minLength, maxLength = min(length1, length2), max(length1, length2)

        if minLength == 0 or maxLength <= 1:
            return 0.0

        symmetricDifferenceCardinality = 0

        for i in range(1, length1):
            self.bag[byte_array1[i-1] & 0xFF][byte_array1[i] & 0xFF] += 1
            symmetricDifferenceCardinality += 1

        for j in range(1, length2):
            bigram_count = self.bag[byte_array2[j-1] & 0xFF][byte_array2[j] & 0xFF] - 1
            self.bag[byte_array2[j-1] & 0xFF][byte_array2[j] & 0xFF] = bigram_count

            if bigram_count >= 0:
                symmetricDifferenceCardinality -= 1
            else:
                symmetricDifferenceCardinality += 1

        for i in range(1, length1):
            self.bag[byte_array1[i-1] & 0xFF][byte_array1[i] & 0xFF] = 0
        for j in range(1, length2):
            self.bag[byte_array2[j-1] & 0xFF][byte_array2[j] & 0xFF] = 0

        rabbit_score = max(1.0 - math.pow(1.2 * symmetricDifferenceCardinality / maxLength, 5.0 / math.log10(maxLength + 1)), 0)
        return rabbit_score * 100

@verificacion_grupos_router.post("/verificacion_grupos", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificar_grupo(nombre_grupo: str, cadena_conexion: ConexionBD, courseid: int = None):
    """
    Verifica si un grupo con el nombre dado existe o si hay grupos similares en Moodle.

    Parámetros:
        - nombre_grupo: Nombre del grupo a verificar.
        - courseid: ID del curso (opcional).

    Retorna:
        - Lista de grupos que tienen una similitud alta con el nombre dado.
    """
    # 1. Verificar si el grupo existe
    grupo_id_respuesta = verificacion_grupo_existe(cadena_conexion, GRUPO=nombre_grupo, COURSEID=courseid)

    if grupo_id_respuesta.status_code == 200:
        grupo_id_body = json.loads(grupo_id_respuesta.body.decode('utf-8'))
        
        if grupo_id_body:
            return {"grupo_id": grupo_id_body}

    # 2. Obtener el listado de grupos si el grupo no existe
    grupos_respuesta = listado_grupos(cadena_conexion, COURSEID=courseid)
    grupos = json.loads(grupos_respuesta.body.decode('utf-8'))

    # 3. Crear una instancia del calculador de similitud
    calculator = StringScoreCalculator()
    grupos_con_puntaje = []

    # 4. Comparar el nombre del grupo con cada grupo en la lista y almacenar los puntajes
    for grupo in grupos:
        puntaje_name = calculator.calculate_similarity_score(nombre_grupo, grupo["name"])
        grupos_con_puntaje.append({"grupo": grupo, "puntaje": puntaje_name})

    # 5. Ordenar los grupos por puntaje de similitud de mayor a menor
    grupos_ordenados = sorted(grupos_con_puntaje, key=lambda x: x["puntaje"], reverse=True)

    # 6. Obtener los 5 grupos con los puntajes más altos
    grupos_top_5 = [grupo["grupo"] for grupo in grupos_ordenados[:5]]

    if grupos_top_5:
        return {"grupos_similares": grupos_top_5}

    # Si no se encontraron grupos, lanzar excepción
    codigo = SIN_GRUPOS
    mensaje = HTTP_MESSAGES.get(codigo)
    raise HTTPException(codigo, mensaje)