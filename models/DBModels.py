from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional

class ConexionBD(BaseModel):
    MOTOR_BD: str
    SERVIDOR: str
    PUERTO: int
    USUARIO: str
    CONTRASENA: str
    NOMBRE_BD: str

class Sesion(BaseModel):
    FECHA_HORA_INICIO: datetime
    FECHA_HORA_FIN: datetime
    FID_USUARIO: int
    FID_CLIENTE: int
    DIALOGO: str
    THREAD_ID: str

class CasoUsoSesion(BaseModel):
    FID_SESION: int
    FID_CASO_USO_CLIENTE: int
    FID_ESTADO_FINAL_CASO_USO: int