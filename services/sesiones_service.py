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
from models.DBModels import Sesion, CasoUsoSesion

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

def create_sesion(sesion: Sesion):
    try:
        with engine.connect() as connection:
            consulta_sql = text("""
                INSERT INTO SESION 
                    (FECHA_HORA_INICIO, FECHA_HORA_FIN, FID_USUARIO, FID_CLIENTE, DIALOGO, THREAD_ID)
                VALUES
                    (:fecha_inicio, :fecha_fin, :id_usuario, :clienteid, :dialogo, :thread);
            """).bindparams(fecha_inicio=sesion.FECHA_HORA_INICIO, fecha_fin=sesion.FECHA_HORA_FIN, id_usuario=sesion.FID_USUARIO,
                            clienteid=sesion.FID_CLIENTE, dialogo=sesion.DIALOGO, thread=sesion.THREAD_ID)
            result = connection.execute(consulta_sql)
            connection.commit()
            sesion_id = result.lastrowid
            return {'ID_SESION': sesion_id}
    except exc.SQLAlchemyError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=e)
    
def create_caso_uso_sesion(casousosesion: CasoUsoSesion):
    try:
        with engine.connect() as connection:
            consulta_sql = text("""
                INSERT INTO `CASO_USO-SESION` 
                    (FID_SESION, `FID_CASO_USO-CLIENTE`, `FID_ESTADO_FINAL-CASO_USO`)
                VALUES
                    ( :sesionid, :casoid, :estado);
            """).bindparams(sesionid=casousosesion.FID_SESION, casoid=casousosesion.FID_CASO_USO_CLIENTE,
                            estado=casousosesion.FID_ESTADO_FINAL_CASO_USO)
            result = connection.execute(consulta_sql)
            connection.commit()
            casosesion_id = result.lastrowid
            return {'ID_CASO_USO_SESION': casosesion_id}
    except exc.SQLAlchemyError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=e)
    
def update_nivel_satisfaccion(NIVEL_SATISFACCION: int, ID_CASO_USO_SESION: int):
    try:
        with engine.connect() as connection:
            consulta_sql = text("""
                UPDATE  `CASO_USO-SESION`
                SET     NIVEL_SATISFACCION =     :nivel_satisfaccion
                WHERE   `ID_CASO_USO-SESION` =    :casosesionid;
            """).bindparams(nivel_satisfaccion=NIVEL_SATISFACCION, casosesionid=ID_CASO_USO_SESION)
            result = connection.execute(consulta_sql)
            connection.commit()
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Registro no encontrado")
            return {'message': 'Datos actualizados'}
    except exc.SQLAlchemyError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=e)
    
def create_retroalimentacion(FID_CASO_USO_SESION: int, TEXTO: str):
    try:
        with engine.connect() as connection:
            consulta_sql = text("""
                INSERT INTO RETROALIMENTACION 
                    (`FID_CASO_USO-SESION`, TEXTO_USUARIO)
                VALUES
                    (:casosesionid, :textousuario);
            """).bindparams(casosesionid=FID_CASO_USO_SESION, textousuario=TEXTO)
            connection.execute(consulta_sql)
            connection.commit()
            return {'message': 'Datos agregados'}
    except exc.SQLAlchemyError as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=e)