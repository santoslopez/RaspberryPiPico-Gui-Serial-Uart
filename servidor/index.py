from flask import Flask, render_template, request, jsonify,g,redirect,url_for,session,flash
from flask_socketio import SocketIO
from errores import ErrorHandlers
from viewsVecino import VecinosView
from enviarMensajes import *
from auth import auth
from puertoSerial import *
from flask_session import Session

from database import nombreBaseDatos
from logger import registroLog

import threading
import sqlite3
import os 

from datetime import datetime

app = Flask(__name__)

obtenerFechaHora = datetime.now()
formatearFecha = obtenerFechaHora.strftime("%d_%m_%_Y _%H:_%M:_%S")

app.config["SECRET_KEY"] = "1234567890"

# almacenar la sesion en el sistema
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(VecinosView)
app.register_blueprint(auth)
app.register_blueprint(ViewMensajes)

socketio = SocketIO(app)
ErrorHandlers.register(app,socketio)
reading_thread = None

@app.route('/listarMensajes',methods=['GET','POST'])
def listarMensajes():
    idUsuarioSes = session.get("idUsuario")
    convertirIDSesion = str(idUsuarioSes)
    
    if not idUsuarioSes:
        # No hay una sesión activa, manejar esto según tus necesidades
        flash("Inicia sesión para acceder a tus mensajes", "info")
        registroLog.info("Necesitas iniciar sesion para acceder al metodo /listarMensajes.")

        return redirect(url_for('login'))

    conexion = sqlite3.connect(nombreBaseDatos)
    cursor = conexion.cursor() 
    cursor.execute("SELECT * FROM mensajes WHERE idUsuario=?",(convertirIDSesion))

    mensajes = cursor.fetchall()
    conexion.close()
    formatoJSON = [{'id':mensaje[0],'tipoMensaje':mensaje[1],'mensaje':mensaje[2],'fecha':mensaje[3],'idUsuario':mensaje[4]} for mensaje in mensajes]
    
    return jsonify({'data': formatoJSON})


@app.route('/listaPuertos',methods=['GET','POST'])
def listaPuertos():
    puertos = obtenerPuertosCOM()    
    if request.method =='POST':
        return render_template("main/puerto.html", puertosCOM=puertos)
    return render_template("main/puerto.html", puertosCOM=puertos)

@app.route('/',methods=['GET','POST'])
def index():
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        return render_template("main/index.html",usuarioSesion=session["usuarioSesion"],idUsuario=idUsuarioSes)
    else:
        flash("No has iniciado sesión")
    return render_template("auth/login.html")

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    global reading_thread
    if reading_thread is None or not reading_thread.is_alive():
        reading_thread = threading.Thread(target=leerPuerto())
        reading_thread.start()
    else:
        print('El hilo ya está en ejecución')

if __name__ == '__main__':
    #app.run(debug=True, port=5000)
    # Obtén el puerto desde el entorno o usa uno predeterminado (5000)
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=True,port=port,host='0.0.0.0')