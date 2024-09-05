import os
import random
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import pytz
from sqlalchemy import create_engine, text, exc
from urllib.parse import quote_plus
from fastapi import APIRouter, HTTPException, Query, Depends
import requests
from datetime import datetime, timedelta
from return_codes import *
from jwt_manager import JWTBearer
from utils.codigo_utils import *

# Cargar variables de entorno
load_dotenv()
usuario = os.getenv("USER_DB_UL")
contrasena = os.getenv("PASS_DB_UL")
host = os.getenv("HOST_DB_UL")
nombre_base_datos = os.getenv("NAME_DB_UL")
token_api = os.getenv("TOKEN_UL_API")

# Codificar la contraseña para la URL de conexión
contrasena_codificada = quote_plus(contrasena)
DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{contrasena_codificada}@{host}/{nombre_base_datos}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def create_verification_code(IDENTIFICACION: int, MOVIL: str, CORREO: str):
    numero_random = random.randint(100000, 999999)
    codigo = hash_code(str(numero_random))
    expiracion = datetime.now(pytz.timezone('America/Bogota')) + timedelta(minutes=3)
    update_verification_code(codigo, expiracion, IDENTIFICACION)
    send_email(CORREO, numero_random)
    send_sms(MOVIL, numero_random)
    return {'message': "Success"}

def verify_code(ID_USUARIO: int, COD_VERIFICACION: str):
    try:
        with engine.connect() as connection:
            consulta_sql = text("""
                SELECT  u.COD_VERIFICACION, u.EXPIRACION_COD
                FROM    USUARIO u 
                WHERE   u.ID_USUARIO = :ID_USUARIO;
            """).bindparams(ID_USUARIO=ID_USUARIO)
            result = connection.execute(consulta_sql)
            row = result.fetchone()
            if row:
                check_code = verify_code_hash(COD_VERIFICACION, row[0])
                naive_dt = row[1]
                aware_dt = pytz.timezone('America/Bogota').localize(naive_dt)
                if check_code and aware_dt > datetime.now(pytz.timezone('America/Bogota')):
                    return {'message': "Success"}
                else:
                    raise HTTPException(status_code=400, detail="Código incorrecto o expirado")
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=e)

def update_verification_code(numero_random: int, expiracion: datetime, IDENTIFICACION: int):
    try:
        with engine.connect() as connection:
            update_sql = text("""
                UPDATE  USUARIO
                SET     COD_VERIFICACION = :codigo,
                        EXPIRACION_COD = :fecha_exp
                WHERE   IDENTIFICACION = (:id);
            """).bindparams(codigo=numero_random, fecha_exp=expiracion, id=IDENTIFICACION)
            result_up = connection.execute(update_sql)
            connection.commit()
            if result_up.rowcount == 0:
                raise HTTPException(status_code=404, detail="Registro no encontrado")
    except exc.SQLAlchemyError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=e)
    
def send_email(CORREO: str, numero_random: int):
    endpoint_url = "https://ulapi-production.up.railway.app/enviar_correos_archivo_adjunto"

    # Datos del correo electrónico
    email_data = {
        "emails": [
            {
                "from_e": "asistentevirtualadminmoodle@univlearning.com",
                "to": CORREO,
                "subject": "Código de verificación del Asistente Virtual",
                "cc": "",
                "html_content": "",
                "content": f"Este código corresponde a la validación del asistente virtual para los coordinadores: {numero_random}"
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token_api}'
    }
    
    try:
        response = requests.post(endpoint_url, json=email_data, headers=headers)
        
        response.raise_for_status()  
        return response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    
    return None

def send_sms(MOVIL: str, numero_random: int):
    endpoint_url = "https://ulapi-production.up.railway.app/send_sms"

    sms_data = {
        "message": f"Este código corresponde a la validación del asistente virtual para los coordinadores: {numero_random}",
        "tpoa": "ul",
        "recipient": [
            {
            "msisdn": MOVIL
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token_api}'
    }

    try:
        response = requests.post(endpoint_url, json=sms_data, headers=headers)
        
        response.raise_for_status()  
        return response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    
    return None