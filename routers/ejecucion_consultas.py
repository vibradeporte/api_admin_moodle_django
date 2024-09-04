from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *
from jwt_manager import JWTBearer
from services.ejecucion_consultas_service import obtener_datos
from services.ejecucion_consultas_service import ConexionBD

ejecucion_consultas_router = APIRouter()

@ejecucion_consultas_router.post("/ejecutar_consulta", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def ejecutar_consulta(cadena_conexion: ConexionBD, consulta: str = Query(...)):
    """
    ## **Descripción:**
        Servicio para ejecutar las sentencias SQL generadas desde el asistente GPT para el caso de uso de reportes.

    ## **Parámetros obligatorios:**
        - consulta -> El código SQL con la consulta para obtener los datos.
        
    ## **Códigos retornados:**
        - 200 -> Los datos se obtuvieron correctamente.
    """
    datos = obtener_datos(consulta, cadena_conexion)
    return JSONResponse(status_code=200, content=datos)