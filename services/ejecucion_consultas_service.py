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
                    row_dict = {}
                    for column, value in zip(column_names, row):
                        if isinstance(value, datetime):
                            row_dict[column] = value.strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(value, Decimal):
                            row_dict[column] = float(value)
                        else:
                            row_dict[column] = value
                    result_dicts.append(row_dict)

                if result_dicts:
                    return result_dicts
                else:
                    raise HTTPException(status_code=404, detail="Datos no encontrados")
        except exc.SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"SQLAlchemy error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    else:
        raise HTTPException(status_code=403, detail="No se ingreso una consulta valida.")
    
def extraer_sql(consulta):
    # Patrón para extraer la consulta SQL entre SELECT y ;
    patron_sql = r"(?i)\bSELECT\b[\s\S]+?;"
    
    # Buscar la consulta SQL en la respuesta
    match = re.search(patron_sql, consulta)
    
    if match:
        return match.group(0).strip()
    else:
        return None  # Si no se encuentra ninguna consulta SQL
