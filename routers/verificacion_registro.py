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

# Crear un enrutador de FastAPI para gestionar las rutas de verificación de registros
verificacion_registro_router = APIRouter()

@verificacion_registro_router.post("/listado_registros", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def listado_registros(cadena_conexion: ConexionBD, COURSEID: int):
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
            SELECT
            DISTINCT subconsulta.Tipo_modulo AS tipo_modulo,
            subconsulta.Nombre_modulo AS nombre_modulo,
            subconsulta.Id_modulo AS id_modulo
        FROM
        (
            SELECT
                c.shortname COLLATE utf8mb4_unicode_ci AS Nombre_Corto_Curso,
                c.fullname COLLATE utf8mb4_unicode_ci AS Nombre_Largo_Curso,
                ccat.name COLLATE utf8mb4_unicode_ci AS Nombre_Categoria,
                cs.name COLLATE utf8mb4_unicode_ci AS Nombre_Seccion,
                m.name COLLATE utf8mb4_unicode_ci AS Tipo_modulo,
                cm.id AS course_modules_id,
                c.id AS course_id,
                COALESCE(
                    rec.id, qz.id, res.id, pg.id, url.id, cert.id, fb.id, frm.id,
                    fld.id, assign.id, lbl.id, scorm.id, survey.id, glos.id, imscp.id,
                    lesson.id, lti.id, wiki.id, wkshop.id, book.id, chat.id, choice.id,
                    data.id, h5p.id, 'No encontrado'
                ) COLLATE utf8mb4_unicode_ci AS Id_modulo,
                COALESCE(
                    rec.name, qz.name, res.name, pg.name, url.name, cert.name, fb.name, frm.name,
                    fld.name, assign.name, lbl.name, scorm.name, survey.name, glos.name, imscp.name,
                    lesson.name, lti.name, wiki.name, wkshop.name, book.name, chat.name, choice.name,
                    data.name, h5p.name, 'No encontrado'
                ) COLLATE utf8mb4_unicode_ci AS Nombre_modulo
            FROM
                mdl_course_sections cs
            JOIN
                mdl_course_modules cm ON cs.id = cm.section
            JOIN
                mdl_course c ON c.id = cm.course
            JOIN
                mdl_course_categories ccat ON ccat.id = c.category
            JOIN
                mdl_modules m ON m.id = cm.module
            LEFT JOIN mdl_reengagement rec ON rec.id = cm.instance AND m.name = 'reengagement'
            LEFT JOIN mdl_quiz qz ON qz.id = cm.instance AND m.name = 'quiz'
            LEFT JOIN mdl_resource res ON res.id = cm.instance AND m.name = 'resource'
            LEFT JOIN mdl_page pg ON pg.id = cm.instance AND m.name = 'page'
            LEFT JOIN mdl_url url ON url.id = cm.instance AND m.name = 'url'
            LEFT JOIN mdl_customcert cert ON cert.id = cm.instance AND m.name = 'customcert'
            LEFT JOIN mdl_feedback fb ON fb.id = cm.instance AND m.name = 'feedback'
            LEFT JOIN mdl_forum frm ON frm.id = cm.instance AND m.name = 'forum'
            LEFT JOIN mdl_folder fld ON fld.id = cm.instance AND m.name = 'folder'
            LEFT JOIN mdl_assign assign ON assign.id = cm.instance AND m.name = 'assign'
            LEFT JOIN mdl_label lbl ON lbl.id = cm.instance AND m.name = 'label'
            LEFT JOIN mdl_scorm scorm ON scorm.id = cm.instance AND m.name = 'scorm'
            LEFT JOIN mdl_survey survey ON survey.id = cm.instance AND m.name = 'survey'
            LEFT JOIN mdl_glossary glos ON glos.id = cm.instance AND m.name = 'glossary'
            LEFT JOIN mdl_imscp imscp ON imscp.id = cm.instance AND m.name = 'imscp'
            LEFT JOIN mdl_lesson lesson ON lesson.id = cm.instance AND m.name = 'lesson'
            LEFT JOIN mdl_lti lti ON lti.id = cm.instance AND m.name = 'lti'
            LEFT JOIN mdl_wiki wiki ON wiki.id = cm.instance AND m.name = 'wiki'
            LEFT JOIN mdl_workshop wkshop ON wkshop.id = cm.instance AND m.name = 'workshop'
            LEFT JOIN mdl_book book ON book.id = cm.instance AND m.name = 'book'
            LEFT JOIN mdl_chat chat ON chat.id = cm.instance AND m.name = 'chat'
            LEFT JOIN mdl_choice choice ON choice.id = cm.instance AND m.name = 'choice'
            LEFT JOIN mdl_data data ON data.id = cm.instance AND m.name = 'data'
            LEFT JOIN mdl_h5pactivity h5p ON h5p.id = cm.instance AND m.name = 'h5pactivity'
            WHERE
                c.id = :COURSEID
            UNION ALL
            SELECT
                c.shortname COLLATE utf8mb4_unicode_ci AS Nombre_Corto_Curso,
                c.fullname COLLATE utf8mb4_unicode_ci AS Nombre_Largo_Curso,
                ccat.name COLLATE utf8mb4_unicode_ci AS Nombre_Categoria,
                NULL AS Nombre_Seccion,
                'group' COLLATE utf8mb4_unicode_ci AS Tipo_modulo,
                NULL AS course_modules_id,
                c.id AS course_id,
                g.id AS Id_modulo,
                g.name COLLATE utf8mb4_unicode_ci AS Nombre_modulo
            FROM
                mdl_course c
            JOIN
                mdl_course_categories ccat ON ccat.id = c.category
            JOIN
                mdl_groups g ON g.courseid = c.id
            WHERE
                c.id = :COURSEID
        ) AS subconsulta;

        """).params(COURSEID=COURSEID)
        
        result = connection.execute(consulta_sql)
        rows = result.fetchall()
        column_names = result.keys()

        result_dicts = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
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


@verificacion_registro_router.post("/verificacion_registro", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def verificacion_registro(nombre_registro: str, cadena_conexion: ConexionBD, courseid: int):
    """
    Verifica si un grupo con el nombre dado existe o si hay grupos similares en Moodle.

    Parámetros:
        - nombre_grupo: Nombre del grupo a verificar.
        - courseid: ID del curso (opcional).

    Retorna:
        - Lista de grupos que tienen una similitud alta con el nombre dado.
    """
    
    # 2. Obtener el listado de grupos si el grupo no existe
    registros_respuesta = listado_registros(cadena_conexion, courseid)
    registros = json.loads(registros_respuesta.body.decode('utf-8'))

    # 3. Crear una instancia del calculador de similitud
    calculator = StringScoreCalculator()
    
    registros_con_puntaje = []
    
    # Convertir `nombre_registro` a minúsculas
    nombre_registro = nombre_registro.lower()

    # 4. Comparar el nombre del grupo con cada grupo en la lista y almacenar los puntajes
    for registro in registros:
        puntaje_name = calculator.calculate_similarity_score(nombre_registro, registro["nombre_modulo"].lower())
        registros_con_puntaje.append({"registro": registro, "puntaje": puntaje_name})
        
    #print(registros_con_puntaje)
    # 5. Ordenar los grupos por puntaje de similitud de mayor a menor
    registros_ordenados = sorted(registros_con_puntaje, key=lambda x: x["puntaje"], reverse=True)

    # 6. Obtener los 5 grupos con los puntajes más altos
    registros_top_5 = [registro["registro"] for registro in registros_ordenados[:5]]

    if registros_top_5:
        #print(registros_top_5)
        return {"registros_similares": registros_top_5}

    # Si no se encontraron datos, lanzar excepción
    codigo = SIN_DATOS
    mensaje = HTTP_MESSAGES.get(codigo)
    raise HTTPException(codigo, mensaje)



