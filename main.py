from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.userlog import userlog_router
from fastapi.staticfiles import StaticFiles
import requests
from routers.verificacion_datos_usuario import verificacion_datos_usuario_router
from routers.verificacion_permisos_usuario import verificacion_permisos_usuario_router
from routers.codigo_verificacion_usuario import codigo_verificacion_usuario_router
from routers.datos_personalizacion_cliente import datos_personalizacion_cliente_router
from routers.verificacion_cursos import verificacion_cursos_router

# Crear una instancia de FastAPI
app = FastAPI()
app.title = "API Asistente para administración de Moodle" # Título de la aplicación
app.version = "0.0.1" # Versión de la aplicación

# Incluir los enrutadores definidos en los módulos de routers
app.include_router(userlog_router)
app.include_router(verificacion_datos_usuario_router)
app.include_router(verificacion_permisos_usuario_router)
app.include_router(codigo_verificacion_usuario_router)
app.include_router(datos_personalizacion_cliente_router)
app.include_router(verificacion_cursos_router)

# Montar la carpeta "static" para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', tags=['home'])
def message():
    """
    Ruta raíz que devuelve un mensaje HTML con la dirección IP del cliente.
    """
    # Hacer una solicitud HTTP GET a 'https://ipinfo.io/ip' para obtener la IP del cliente
    response = requests.get('https://ipinfo.io/ip')
    ip_address = response.text.strip()# Obtener la IP del cliente de la respuesta y eliminar espacios en blanco
    print(ip_address)# Imprimir la IP del cliente en la consola
    return HTMLResponse(f'<h1>API Asistente para administración de Moodle</h1><p>Client IP: {ip_address}</p>')
  # Devolver una respuesta HTML con el título de la aplicación y la IP del cliente

 

