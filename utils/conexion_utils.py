from sqlalchemy import create_engine
from urllib.parse import quote_plus
from models.DBModels import ConexionBD

def create_connection(cadena_conexion: ConexionBD):
    encoded_password = quote_plus(cadena_conexion.CONTRASENA)
    encoded_user = quote_plus(cadena_conexion.USUARIO)
    encoded_bd = quote_plus(cadena_conexion.NOMBRE_BD)
        
    cadena_conexion_f = f"{cadena_conexion.MOTOR_BD}://{encoded_user}:{encoded_password}@{cadena_conexion.SERVIDOR}:{cadena_conexion.PUERTO}/{encoded_bd}"
    return create_engine(cadena_conexion_f, pool_pre_ping=True)