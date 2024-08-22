from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from datetime import datetime
from return_codes import *
from jwt_manager import JWTBearer
from services.codigo_verificacion_service import create_verification_code, verify_code

codigo_verificacion_usuario_router = APIRouter()

@codigo_verificacion_usuario_router.post("/crear_codigo_verificacion_usuario", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def crear_codigo_verificacion_usuario(IDENTIFICACION: int, MOVIL: str = Query(), CORREO: str = Query()):
    """
    ## **Descripción:**
        Servicio para crear el código de verificación en la base de datos para el usuario consultado y enviarselo por correo y sms.

    ## **Parámetros obligatorios:**
        - IDENTIFICACION -> Corresponde al número de cedula del usuario.
        - MOVIL -> Número de telefono del usuario.
        - CORREO -> Correo electronico del usuario.
        
    ## **Códigos retornados:**
        - 200 -> El código se genero y se envio correctamente al usuario.
    """
    status = create_verification_code(IDENTIFICACION, MOVIL, CORREO)
    return JSONResponse(status_code=200, content=status)

@codigo_verificacion_usuario_router.post("/check_codigo_verificacion_usuario", tags=['Caso_uso_reportes'], status_code=200, dependencies=[Depends(JWTBearer())])
def check_codigo_verificacion_usuario(IDENTIFICACION: int, COD_VERIFICACION: str):
    """
    ## **Descripción:**
        Servicio para verificar que el código ingresado por el usuario corresponda con el que esta guardado en la base de datos.

    ## **Parámetros obligatorios:**
        - IDENTIFICACION -> Corresponde al número de cedula del usuario.
        - COD_VERIFICACION -> Código que el usuario ingreso para compararlo con el que esta en la base de datos.
        
    ## **Códigos retornados:**
        - 200 -> El código ingresado por el usuario es correcto
    """
    check_code = verify_code(IDENTIFICACION, COD_VERIFICACION)
    return JSONResponse(status_code=200, content=check_code)