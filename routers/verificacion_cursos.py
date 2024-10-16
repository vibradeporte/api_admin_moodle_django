import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Depends
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

# Crear un enrutador de FastAPI para gestionar las rutas de verificación de cursos
verificacion_cursos_router = APIRouter()

@verificacion_cursos_router.post("/verificacion_curso_existe", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_curso_existe(CURSO: str, cadena_conexion: ConexionBD):
    """
    ## **Descripción:**
        Verifica si un curso con el nombre dado existe en Moodle.

    ## **Parámetros obligatorios:**
        - CURSO -> Nombre del curso (largo o corto).
       
    ## **Campos retornados:**
        - CURSOS -> Lista de cursos que coinciden con el nombre dado.
    """
    CURSO = CURSO.lower()  # Convertir a minúsculas
    engine = create_connection(cadena_conexion)
    with engine.connect() as connection:
        consulta_sql = text(""" 
            SELECT DISTINCT c.id 
            FROM mdl_course c 
            WHERE LOWER(c.shortname) = :CURSO OR LOWER(c.fullname) = :CURSO;
        """).params(CURSO=CURSO)
        
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = [dict(zip(column_names, row)) for row in rows]

        return JSONResponse(content=result_dicts)





@verificacion_cursos_router.post("/listado_cursos", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def listado_cursos(cadena_conexion: ConexionBD):
    """
    ## **Descripción:**
        Obtiene el nombre largo y corto de todos los cursos en Moodle.

    ## **Códigos retornados:**
        - 200 -> Listado de cursos en Moodle.

    ## **Campos retornados:**
        - id -> Id del curso.
        - fullname -> Nombre largo del curso.
        - shortname -> Nombre corto del curso.
        - summary -> Resumen del curso en texto plano.
    """
    engine = create_connection(cadena_conexion)
    with engine.connect() as connection:
        consulta_sql = text("""
            SELECT DISTINCT c.id, c.fullname, c.shortname, c.summary
            FROM mdl_course c;
        """)
        
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            # Convertir el campo summary de HTML a texto plano
            if row_dict.get('summary'):
                soup = BeautifulSoup(row_dict['summary'], 'html.parser')
                row_dict['summary'] = soup.get_text()
            result_dicts.append(row_dict)

        return JSONResponse(content=result_dicts)




class StringScoreCalculator:
    def __init__(self):
        self.bag = np.zeros((256, 256))

    def calculate_similarity_score(self, array1, array2):
        if not isinstance(array1, str) or not isinstance(array2, str):
            return 0.0

        byte_array1 = array1.encode('utf-8')
        byte_array2 = array2.encode('utf-8')

        return self._calculate_similarity_score(byte_array1, byte_array2)

    def _calculate_similarity_score(self, byte_array1, byte_array2):
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

@verificacion_cursos_router.post("/verificacion_cursos", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificar_curso(nombre_curso: str, cadena_conexion: ConexionBD):
    """
    ## **Descripción:**
        Verifica si un curso con el nombre dado existe o si hay cursos similares en Moodle.

    ## **Parámetros obligatorios:**
        - nombre_curso -> Nombre del curso a verificar.

    ## **Campos retornados:**
        - cursos_similares -> Lista de cursos que tienen una similitud alta con el nombre dado.
    """
    # Convertir el nombre del curso a minúsculas
    nombre_curso = nombre_curso.lower()

    # 1. Verificar si el curso existe
    curso_id_respuesta = verificacion_curso_existe(nombre_curso, cadena_conexion)

    if curso_id_respuesta.status_code == 200:
        curso_id_body = json.loads(curso_id_respuesta.body.decode('utf-8'))
        
        if curso_id_body:
            return {"curso_id": curso_id_body}

    # 2. Obtener el listado de cursos si el curso no existe
    cursos_respuesta = listado_cursos(cadena_conexion)
    cursos = json.loads(cursos_respuesta.body.decode('utf-8'))

    # 3. Crear una instancia del calculador de similitud
    calculator = StringScoreCalculator()
    cursos_con_puntaje = []

    # 4. Comparar el nombre del curso con cada curso en la lista y almacenar los puntajes
    for curso in cursos:
        # Convertir los nombres de los cursos a minúsculas para la comparación
        puntaje_fullname = calculator.calculate_similarity_score(nombre_curso, curso["fullname"].lower())
        puntaje_shortname = calculator.calculate_similarity_score(nombre_curso, curso["shortname"].lower())
        
        mejor_puntaje = max(puntaje_fullname, puntaje_shortname)
        
        cursos_con_puntaje.append({"curso": curso, "puntaje": mejor_puntaje})

    # 5. Ordenar los cursos por puntaje de similitud de mayor a menor
    cursos_ordenados = sorted(cursos_con_puntaje, key=lambda x: x["puntaje"], reverse=True)

    # 6. Obtener los 5 cursos con los puntajes más altos
    cursos_top_5 = [curso["curso"] for curso in cursos_ordenados[:5]]

    if cursos_top_5:
        return {"cursos_similares": cursos_top_5}

    codigo = SIN_CURSOS
    mensaje = HTTP_MESSAGES.get(codigo)
    raise HTTPException(codigo, mensaje)

