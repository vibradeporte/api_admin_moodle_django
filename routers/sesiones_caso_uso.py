from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from models.DBModels import Sesion
from models.DBModels import CasoUsoSesion
from return_codes import *
from jwt_manager import JWTBearer
from services.sesiones_service import *

sesiones_caso_uso_router = APIRouter()

@sesiones_caso_uso_router.post("/crear_sesion", tags=['Caso_uso_reportes'], status_code=201, dependencies=[Depends(JWTBearer())])
def crear_sesion(sesion: Sesion):
    """
    ## **Descripción:**
        Servicio para crear una sesión, en la tabla SESION en la base de datos con los datos obtenidos a lo largo de la conversación.

    ## **Parámetros obligatorios:**
        - FECHA_HORA_INICIO -> Fecha y hora de inicio de la conversación entre el usuario y el asistente.
        - FECHA_HORA_FIN -> Fecha y hora de finalizacion de la conversación entre el usuario y el asistente.
        - FID_USUARIO -> Id del usuario en la base de datos.
        - FID_CLIENTE -> Id del cliente en la base de datos.
        - DIALOGO -> Todos los mensajes que se enviarion en la conversación, tanto del asistente como del usuario.
        - THREAD_ID -> Id del hilo de la conversación en la plataforma de OpenAI.
        
    ## **Códigos retornados:**
        - 201 -> Los datos se ingresaron correctamente.
    """
    sesion = create_sesion(sesion)
    return JSONResponse(status_code=201, content=sesion)

@sesiones_caso_uso_router.post("/crear_caso_uso_sesion", tags=['Caso_uso_reportes'], status_code=201, dependencies=[Depends(JWTBearer())])
def crear_caso_uso_sesion(casousosesion: CasoUsoSesion):
    """
    ## **Descripción:**
        Servicio para guardar el caso de uso de una sesión, en la tabla CASO_USO-SESION.

    ## **Parámetros obligatorios:**
        - FID_SESION -> Id de la sesión creada para la conversación.
        - FID_CASO_USO_CLIENTE -> Id del caso de uso para el cliente.
        - FID_ESTADO_FINAL_CASO_USO -> Id del estado final con el que termino la conversación.
        
    ## **Códigos retornados:**
        - 201 -> Los datos se ingresaron correctamente.
    """
    caso_sesion = create_caso_uso_sesion(casousosesion)
    return JSONResponse(status_code=201, content=caso_sesion)

@sesiones_caso_uso_router.put("/actualizar_nivel_satisfaccion", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def actualizar_nivel_satisfaccion(NIVEL_SATISFACCION: int, ID_CASO_USO_SESION: int):
    """
    ## **Descripción:**
        Actualiza un registro de la tabla CASO_USO-SESION agregando el nivel de satisfaccion del usuario.

    ## **Parámetros obligatorios:**
        - ID_CASO_USO_SESION -> Id del caso uso sesion.
        - NIVEL_SATISFACCION -> Nivel de satisfaccion del usuario de 1 a 5.

     ## **Códigos retornados:**
        - 200 -> La operación se realizó correctamente.
    """
    status = update_nivel_satisfaccion(NIVEL_SATISFACCION, ID_CASO_USO_SESION)
    return JSONResponse(status_code=200, content=status)

@sesiones_caso_uso_router.post("/crear_retroalimentacion", tags=['Caso_uso_reportes'], status_code=201, dependencies=[Depends(JWTBearer())])
def crear_retroalimentacion(FID_CASO_USO_SESION: int, TEXTO: str = Query(...)):
    """
    ## **Descripción:**
        Servicio para crear un registro en la tabla RETROALIMENTACION.

    ## **Parámetros obligatorios:**
        - FID_CASO_USO-SESION -> Id del caso de uso de la sesión.
        - TEXTO -> Retroalimentción del usuario
        
    ## **Códigos retornados:**
        - 201 -> Los datos se ingresaron correctamente.
    """
    retroalimentacion = create_retroalimentacion(FID_CASO_USO_SESION, TEXTO)
    return JSONResponse(status_code=201, content=retroalimentacion)