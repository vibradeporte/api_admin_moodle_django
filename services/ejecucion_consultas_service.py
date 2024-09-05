import os
import re
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text, exc
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends
from return_codes import *
from jwt_manager import JWTBearer
from utils.codigo_utils import *
from datetime import datetime

# Cargar variables de entorno
load_dotenv()
usuario = os.getenv("USER_DB_RO")
contrasena = os.getenv("PASS_DB_RO")
host = os.getenv("HOST_DB_RO")
nombre_base_datos = os.getenv("NAME_DB_RO")
token_api = os.getenv("TOKEN_UL_API")

# Codificar la contraseña para la URL de conexión
contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def obtener_datos(consulta):
    codigo_sql = extraer_sql(consulta)
    if codigo_sql:
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
                    
                    # Convertir datetime a string para serializar
                    for key, value in row_dict.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()

                    result_dicts.append(row_dict)

                if result_dicts:
                    return result_dicts
                else:
                    raise HTTPException(status_code=200, detail="El resultado de la consulta es vacío.")
        except exc.SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))
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
