from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.userlog import userlog_router

from fastapi.staticfiles import StaticFiles
import requests
from routers.verificacion_datos_usuario import verificacion_datos_usuario_router
from routers.verificacion_permisos_usuario import verificacion_permisos_usuario_router



app = FastAPI()
app.title = "API Asistente para administración de Moodle"
app.version = "0.0.1"

app.include_router(userlog_router)

app.include_router(verificacion_datos_usuario_router)
app.include_router(verificacion_permisos_usuario_router)



app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', tags=['home'])
def message():
    response = requests.get('https://ipinfo.io/ip')
    ip_address = response.text.strip()
    print(ip_address)
    return HTMLResponse(f'<h1>API Asistente para administración de Moodle</h1><p>Client IP: {ip_address}</p>')
