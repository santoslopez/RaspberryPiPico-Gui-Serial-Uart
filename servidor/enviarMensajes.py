from flask import render_template, request, flash, session,Blueprint

from puertoSerial import PUERTO_DEFAULT,serial_port,abrirPuerto
from database import nombreBaseDatos
from logger import registroLog
from datetime import datetime
from auth import login_requerido

import sqlite3

ViewMensajes = Blueprint('ViewMensajes',__name__)

def obtenerVecinos():
    conexion = sqlite3.connect(nombreBaseDatos)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("select * from vecinos")
    vecinos = cursor.fetchall()
    # convertir a diccionario
    diccionarioVecinos = [dict(vecinos) for vecinos in vecinos]
    conexion.close()    
    return diccionarioVecinos

def obtenerUltimoIDMensaje():
    conexion = sqlite3.connect(nombreBaseDatos)
    cursor = conexion.cursor()
    consulta = "SELECT printf('%02d',MAX(id)) AS id FROM mensajes"
    cursor.execute(consulta)
    resultado = cursor.fetchone()
    
    if resultado is not None and resultado[0] is not None:
        idMaximo = resultado[0]
        return idMaximo
    else:
        conexion.close()
        return 0

@ViewMensajes.route('/formularioEnvioMensaje',methods=['GET','POST'])

def formularioEnvioMensaje():
    obtenerDatos = obtenerVecinos()
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        return render_template("main/enviarMensaje.html",listadoVecinos=obtenerDatos,usuarioSesion=session["usuarioSesion"],idUsuario=idUsuarioSes)    
    else:
        flash("No has iniciado sesión")
        return render_template("auth/login.html")

# Ruta de Flask para enviar mensajes
@ViewMensajes.route('/enviarMensajeInicial', methods=['POST'])
# Ruta de Flask para enviar mensajes
def enviarMensajeInicial():
    if "usuarioSesion" in session:
        try:
            if serial_port.is_open:
                if request.method == "POST":
                    idUsuarioSes = session["idUsuario"]
                    mensajeINIT = "INIT"
                    hostEmisor = request.form.get("txtHostEmisor")
                    # validar 
                    if not hostEmisor:
                        flash("Debes ingresar un usuario y una contraseña","error")
                     
                        return "noguardado"
                    else:
                        mensajeCompleto = f"{hostEmisor}|{mensajeINIT}"
                        obtenerFechaHora = datetime.now()
                        formatearFecha = obtenerFechaHora.strftime("%d/%m/%Y %H:%M:%S")
                        # convertir a entero
                        idUsu = int(idUsuarioSes)
                        with sqlite3.connect(nombreBaseDatos) as conexion:
                            cursor = conexion.cursor()
                            cursor.execute("INSERT INTO mensajes(tipoMensaje,mensaje,fecha,idUsuario) VALUES (?,?,?,?)",
                                        ("Enviado",mensajeINIT,formatearFecha,idUsu))
                            conexion.commit()
                            registroLog.info(f"El mensaje: {mensajeCompleto} se ha enviado al receptor.")

                            serial_port.write(mensajeCompleto.encode('utf-8'))

                        return "guardado"

                else:
                    return "noguardado"
            else:
                abrirPuerto(PUERTO_DEFAULT)
                return "puertocerrado"

        except Exception as e:
        
            print("Error en el envío del mensaje: ",{e})
            return "Error en el envío del mensaje {e}"
    else:
        flash("No has iniciado sesión")
        return render_template("auth/login.html")

# Ruta de Flask para enviar mensajes
@ViewMensajes.route('/enviarMensaje', methods=['POST'])
def enviarMensaje():
    if "usuarioSesion" in session:
        try:
            if serial_port.is_open:
                if request.method == "POST":
                    idUsuarioSes = session["idUsuario"]
                    mensaje = request.form.get("txtEnviarMensaje")
                    hostEmisor = request.form.get("txtHostEmisor")
                    hostReceptor = request.form.get("selectVecinos")
                    # validar 
                    if not hostReceptor or not  hostEmisor or not mensaje:
                        flash("Debes ingresar un usuario y una contraseña","error")
                        return "noguardado"
                    else:
                        idMensaje = obtenerUltimoIDMensaje()
                        idMe = str(idMensaje)
                        hasBeenReceived = "0"

                        mensajeCompleto = f"{hostEmisor}|{hostReceptor}|{idMe}|{hasBeenReceived}|{mensaje}"

                        obtenerFechaHora = datetime.now()
                        formatearFecha = obtenerFechaHora.strftime("%d/%m/%Y %H:%M:%S")
                        # convertir a entero
                        idUsu = int(idUsuarioSes)
                        with sqlite3.connect(nombreBaseDatos) as conexion:
                            cursor = conexion.cursor()
                            cursor.execute("INSERT INTO mensajes(tipoMensaje,mensaje,fecha,idUsuario) VALUES (?,?,?,?)",
                                        ("Enviado", mensajeCompleto, formatearFecha,idUsu))
                            conexion.commit()
                            registroLog.info(f"El mensaje: {mensajeCompleto} se ha enviado al receptor.")

                            serial_port.write(mensajeCompleto.encode('utf-8'))

                        return "guardado"

                else:
                    return "noguardado"
            else:
                abrirPuerto(PUERTO_DEFAULT)
                return "puertocerrado"
                #formatoJSON = {'success': False, 'mensaje': "Verifica que esté habilitado el puerto de serial"}
                #return jsonify({'data': formatoJSON})

        except Exception as e:
            print("Error en el envío del mensaje {e}")
            return "Error en el envío del mensaje {e}"
    else:
        flash("No has iniciado sesión")
        return render_template("auth/login.html")