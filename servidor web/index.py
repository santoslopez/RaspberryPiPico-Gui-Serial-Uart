from flask import Flask, render_template, request, jsonify,g,redirect,url_for,session,flash
from flask_socketio import SocketIO
from errores import ErrorHandlers
from viewsVecino import VecinosView
from flask_session import Session

import serial
import serial.tools.list_ports
import threading
import logging
import sqlite3
#import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
#from flask_sqlaclhemy import SQLAlchemy

app = Flask(__name__)


obtenerFechaHora = datetime.now()
formatearFecha = obtenerFechaHora.strftime("%d_%m_%_Y _%H:_%M:_%S")

nombreLog = "app.log"
# configurar registro de sistema
logging.basicConfig(filename=nombreLog,level=logging.DEBUG)
# realizar el registro de los errores
registroLog = logging.getLogger("index")
app.config["SECRET_KEY"] = "1234567890"

# almacenar la sesion en el sistema
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.register_blueprint(VecinosView)


socketio = SocketIO(app)

ErrorHandlers.register(app,socketio)
serial_port = serial.Serial()
reading_thread = None

valorBaudarate = 9600
'''
Se utiliza este puerto para hacer la comunicacion del cable usb a serial UART.
De está forma se puede enviar y recibir datos desde el servidor web a la raspberry pi pico
'''

PUERTO_DEFAULT = "/dev/cu.usbserial-0001"

nombreBaseDatos = "database.db"


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
    
def obtenerPuertosCOM():
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    return com_ports


def abrirPuerto(puerto):
    try:
        if serial_port.is_open:
            serial_port.close()
        serial_port.port=puerto
        serial_port.baudrate=valorBaudarate
        serial_port.open()

        return True,"Puerto abierto correctamente"
    except Exception as e:
        registroLog .info(f"Error al abrir el puerto: {puerto(e)}")
        return False,f"Error al abrir el puerto: {puerto(e)}"

def leerPuerto(session):

    while True:
        
        if serial_port.is_open and serial_port.in_waiting > 0:
            line = serial_port.readline().decode('utf-8')
            #line2 = serial_port.readline()
            #print("obtuve esto: ",line)
            
            cadenaEnviar = str(line)
            hostEmisorR=cadenaEnviar[0:3]
            # se obtiene el primer |
            simboloOR1R=cadenaEnviar[3:4]
            hostReceptorR=cadenaEnviar[4:7]
            # se obtiene el segundo |
            simboloOR2R=cadenaEnviar[7:8]
            # idMensaje
            idMensajeR = cadenaEnviar[8:10].zfill(2)
            #print("idMensajeR: "+str(idMensajeR))
            simboloOR3R = cadenaEnviar[10:11]
            hasBeenReceivedR = cadenaEnviar[11:12]
            simboloR4R= cadenaEnviar[12:13]                
            mensajeCompletoR= cadenaEnviar[13:20]    

            mensajeEnviar = hostEmisorR+simboloOR1R+hostReceptorR+simboloOR2R+idMensajeR+simboloOR3R+hasBeenReceivedR+simboloR4R+mensajeCompletoR
            
            obtenerFechaHora = datetime.now()
            formatearFecha = obtenerFechaHora.strftime("%d/%m/%Y %H:%M:%S")
            

            #idUsuario = session.get("idUsuario", None)

            
            try:
                conexion = sqlite3.connect(nombreBaseDatos)
                cursor = conexion.cursor()
                
                # recuperar sesion de idUsuario
                if "usuarioSesion" in session:
                
                    #idUsuario=session["idUsuario"]
                    idUsuarioSes = session.get("idUsuario")

                    #idUsuario = session.get("idUsuario")
                    cursor.execute("insert into mensajes(tipoMensaje,mensaje,fecha,idUsuario) values (?, ?, ?,?)", ("Recibido",cadenaEnviar,formatearFecha,idUsuarioSes))
                    conexion.commit()
                    registroLog.info(f"Se recibio el mensaje: {mensajeEnviar} y se almaceno en la base de datos.")
                else:
                    print("estoy aquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkkaquiiiiiiiizxxxkk")
            except sqlite3.Error as e:
                print(f"Error al insertar en la base de datos: {e}")
                registroLog.info("Se produjo un error al querer insertar a la base de datos. El mensaje recibido es: {mensajeEnviar}")

            socketio.emit('datos_actualizados', {'data': line})
        else:
            puerto = "/dev/cu.usbserial-0001"
            #abrirPuerto(puerto)
            #print("El puerto no esta abierto o no hay datos")
            
        socketio.sleep(0.001)
        #socketio.sleep(0)


@app.route('/listaPuertos',methods=['GET','POST'])
def listaPuertos():
    puertos = obtenerPuertosCOM()    
    if request.method =='POST':
        puerto = request.form['puerto']

        return render_template("puerto.html", puertosCOM=puertos)

    return render_template("puerto.html", puertosCOM=puertos)


@app.route('/',methods=['GET','POST'])
def index():
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]

        return render_template("index.html",usuarioSesion=session["usuarioSesion"],idUsuario=idUsuarioSes)
    else:
        flash("No has iniciado sesión")
    return render_template("login.html")
       
@app.route('/fmrLogin',methods=['GET','POST'])
def frmLogin():
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        return render_template("index.html",idUsuario=idUsuarioSes,usuarioSesion=session["usuarioSesion"])
    else:
        flash("No has iniciado sesión")
        registroLog.info("El usuario no ha iniciado sesion redirigido al login.")
        return render_template("login.html")
    
@app.route('/frmRegistroCuenta',methods=['GET','POST'])
def frmRegistroCuenta():
    return render_template("frmRegistroCuenta.html")

@app.route('/registroCuenta',methods=["POST"])
def registroCuenta():
    if request.method == "POST":
        usuarioGuardar = request.form.get("txtUsuario")
        passwordGuardar = request.form.get("txtPassword")
        
        if not usuarioGuardar or not passwordGuardar:
            flash("Debes ingresar un usuario y una contraseña","error")
            return render_template("frmRegistroCuenta.html")
        else:
            with sqlite3.connect(nombreBaseDatos) as conexion:
                cursor = conexion.cursor()
                cursor.execute("INSERT INTO usuarios(usuario,password) VALUES (?, ?)",(usuarioGuardar,passwordGuardar))
                conexion.commit()
                registroLog.info("El usuario se ha guardado correctamente.")

                return render_template("registroExitoso.html")
    else:
        return render_template("frmRegistroCuenta.html")
    
# cerrar la sesion del usuario
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop("usuarioSesion",None)
    flash("Se ha cerrado la sesion correctamente","sucess")
    return redirect(url_for("frmLogin"))

@app.route('/listarMensajes',methods=['GET','POST'])
def listarMensajes():
    idUsuarioSes = session.get("idUsuario")
    convertirIDSesion = str(idUsuarioSes)
    #print("El ide del usuario es XXXXXXXXXXXXXXXXXXXXXX: "+convertirIDSesion)
    
    if not idUsuarioSes:
        # No hay una sesión activa, manejar esto según tus necesidades
        flash("Inicia sesión para acceder a tus mensajes", "info")
        registroLog.info("Necesitas iniciar sesion para acceder al metodo /listarMensajes.")

        return redirect(url_for('login'))
    
    
    conexion = sqlite3.connect(nombreBaseDatos)
    #print("estoy aquiestoy aquiestoy aquiestoy aquiestoy aqui: "+idUsuarioSes)
    print("Opened database successfully")
    cursor = conexion.cursor() 
    cursor.execute("SELECT * FROM mensajes WHERE idUsuario=?",(convertirIDSesion))

    mensajes = cursor.fetchall()
    conexion.close()
    formatoJSON = [{'id':mensaje[0],'tipoMensaje':mensaje[1],'mensaje':mensaje[2],'fecha':mensaje[3],'idUsuario':mensaje[4]} for mensaje in mensajes]
    
    return jsonify({'data': formatoJSON})

def obtenerVecinos():
    conexion = sqlite3.connect(nombreBaseDatos)
    print("Opened database successfully")
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()
    cursor.execute("select * from vecinos")
    vecinos = cursor.fetchall()
    
    # convertir a diccionario
    diccionarioVecinos = [dict(vecinos) for vecinos in vecinos]

    print(vecinos)
    conexion.close()
    
    return diccionarioVecinos



@app.route('/login',methods=['POST'])
def login():
    # Verificar si ya hay una sesión activa
    if "usuarioSesion" in session:
        # Ya hay una sesión activa, redirigir a la página principal
        flash("Ya tienes una sesión activa", "info")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        usuario = request.form.get("txtUsuario")
        print("estoy aqui: "+usuario)
        passwordGuardar = request.form.get("txtPassword")

        # validar usuario y password por medio de la base de datos sqlite
        conexion = sqlite3.connect(nombreBaseDatos)
        cursor = conexion.cursor()
        cursor.execute("select * from usuarios where usuario=? and password=?",(usuario,passwordGuardar,))
        ejecutar = cursor.fetchall()
        conexion.close()

        # validar que el usuario y password sean correctos
        if len(ejecutar) > 0:
            # se crea la sesion de que existe el usuario
            
            session["usuarioSesion"]=usuario
            # se accede al primer resultado y primera columna
            session["idUsuario"]=ejecutar[0][0]
            #session["usuarioSesion2"]=ejecutar[0][1]


            usuarioSes = session["usuarioSesion"]
            
            idUsuarioSes = session["idUsuario"]
            #usuarioSes2 = session["usuarioSesion2"]


            flash("Inicio de sesion exitoso", "success")
            #return render_template("index.html")
            #return redirect(url_for('index'))
            return render_template("index.html",registroExitoso=True,usuarioSesion=usuarioSes,idUsuario=idUsuarioSes)
        else:
            flash("Usuario o contraseña incorrectos","error")
            return render_template("login.html",registroExitoso=False)

@app.route('/formularioEnvioMensaje',methods=['GET','POST'])
def formularioEnvioMensaje():
    obtenerDatos = obtenerVecinos()
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        #return render_template("index.html",usuarioSesion=session["usuarioSesion"])
        return render_template("enviarMensaje.html",listadoVecinos=obtenerDatos,usuarioSesion=session["usuarioSesion"],idUsuario=idUsuarioSes)    
    else:
        flash("No has iniciado sesión")
        return render_template("login.html")
    

# Ruta de Flask para enviar mensajes
@app.route('/enviarMensaje', methods=['POST'])
def enviarMensaje():
    if "usuarioSesion" in session:
        try:
            abrirPuerto(PUERTO_DEFAULT)
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
                return "puertocerrado"
                #formatoJSON = {'success': False, 'mensaje': "Verifica que esté habilitado el puerto de serial"}
                #return jsonify({'data': formatoJSON})

        except Exception as e:
        
            print("Error en el envío del mensaje")
            return "enexception"
    

    else:
        flash("No has iniciado sesión")
        return render_template("login.html")


@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    global reading_thread
    if reading_thread is None or not reading_thread.is_alive():
        reading_thread = threading.Thread(target=leerPuerto(session))
        reading_thread.start()
    else:
        print('El hilo ya está en ejecución')


if __name__ == '__main__':
    abrirPuerto(PUERTO_DEFAULT)

    #app.run(debug=True, port=5000)
    socketio.run(app, debug=True,port=5000,host='0.0.0.0')