import os
import re
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text, exc
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends
from return_codes import *
from jwt_manager import JWTBearer
from utils.codigo_utils import *
from utils.conexion_utils import create_connection
from models.DBModels import ConexionBD

def obtener_datos(consulta, cadena_conexion: ConexionBD):
    codigo_sql = extraer_sql(consulta)
    if codigo_sql:
        engine = create_connection(cadena_conexion)
        try:
            with engine.connect() as connection:
                consulta_sql = text(f"""
                    {codigo_sql}
                """)
                result = connection.execute(consulta_sql)
                rows = result.fetchall()
                column_names = result.keys()

                result_dicts = []
                for row in rows:
                    row_dict = dict(zip(column_names, row))
                    result_dicts.append(row_dict)

                if result_dicts:
                    return result_dicts
                else:
                    raise HTTPException(status_code=400, detail="Datos no encontrados")
        except exc.SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=e)
    else:
        raise HTTPException(status_code=401, detail="No se ingreso una consulta valida.")
    
def extraer_sql(consulta):
    # Patrón para extraer la consulta SQL entre SELECT y ;
    patron_sql = r"(?i)\bSELECT\b[\s\S]+?;"
    
    # Buscar la consulta SQL en la respuesta
    match = re.search(patron_sql, consulta)
    
    if match:
        return match.group(0).strip()
    else:
        return None  # Si no se encuentra ninguna consulta SQL