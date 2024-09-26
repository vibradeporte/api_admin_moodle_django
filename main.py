from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.userlog import userlog_router

from fastapi.staticfiles import StaticFiles
import requests
from routers.verificacion_datos_usuario import verificacion_datos_usuario_router
from routers.verificacion_permisos_usuario import verificacion_permisos_usuario_router
from routers.codigo_verificacion_usuario import codigo_verificacion_usuario_router
from routers.ejecucion_consultas import ejecucion_consultas_router
from routers.datos_personalizacion_cliente import datos_personalizacion_cliente_router
from routers.verificacion_cursos import verificacion_cursos_router
from routers.sesiones_caso_uso import sesiones_caso_uso_router
from routers.verificacion_grupos import verificacion_grupos_router



app = FastAPI()
app.title = "API Asistente para administración de Moodle"
app.version = "0.0.1"

app.include_router(userlog_router)

app.include_router(verificacion_datos_usuario_router)
app.include_router(verificacion_permisos_usuario_router)

app.include_router(codigo_verificacion_usuario_router)

app.include_router(datos_personalizacion_cliente_router)
app.include_router(verificacion_cursos_router)

app.include_router(ejecucion_consultas_router)

app.include_router(sesiones_caso_uso_router)

app.include_router(verificacion_grupos_router)



#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', tags=['home'])
def message():
    response = requests.get('https://ipinfo.io/ip')
    ip_address = response.text.strip()
    print(ip_address)
    return HTMLResponse(f'<h1>API Asistente para administración de Moodle</h1><p>Client IP: {ip_address}</p>')
