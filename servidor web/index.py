from flask import Flask, render_template, request, jsonify,g,redirect,url_for
from flask_socketio import SocketIO
from errores import ErrorHandlers
from viewsVecino import VecinosView

import serial
import serial.tools.list_ports
import threading

import sqlite3
#import os
from datetime import datetime
app = Flask(__name__)

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

        return False,f"Error al abrir el puerto: {puerto(e)}"

def leerPuerto():
    while True:
        if serial_port.is_open and serial_port.in_waiting > 0:
            line = serial_port.readline().decode('utf-8')
            #line2 = serial_port.readline()
            
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
            mensajeCompletoR= cadenaEnviar[13:20].strip()    

            mensajeEnviar = hostEmisorR+simboloOR1R+hostReceptorR+simboloOR2R+idMensajeR+simboloOR3R+hasBeenReceivedR+simboloR4R+mensajeCompletoR
            
            obtenerFechaHora = datetime.now()
            formatearFecha = obtenerFechaHora.strftime("%d/%m/%Y %H:%M:%S")

            try:
                conexion = sqlite3.connect(nombreBaseDatos)
                cursor = conexion.cursor()
                
                cursor.execute("insert into mensajes(tipoMensaje,mensaje,fecha) values (?, ?, ?)", ("Recibido",mensajeEnviar,formatearFecha))
                conexion.commit()
                socketio.emit('datos_actualizados', {'data': line})
            except sqlite3.Error as e:
                print(f"Error al insertar en la base de datos: {e}")
            finally:
                if cursor:
                    cursor.close()
                if conexion:
                    conexion.close()

        #else:
        #puerto = "/dev/cu.usbserial-0001"
        #abrirPuerto(puerto)
        #    print("El puerto no esta abierto o no hay datos")
            
        #socketio.sleep(0)
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
    return render_template("index.html")
       

@app.route('/listarMensajes',methods=['GET','POST'])
def listarMensajes():
    conexion = sqlite3.connect(nombreBaseDatos)
    print("Opened database successfully")
    cursor = conexion.cursor()
    consulta = "SELECT * FROM mensajes"
    cursor.execute(consulta)

    mensajes = cursor.fetchall()
    conexion.close()
    formatoJSON = [{'id':mensaje[0],'tipoMensaje':mensaje[1],'mensaje':mensaje[2],'fecha':mensaje[3]} for mensaje in mensajes]
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

@app.route('/formularioEnvioMensaje',methods=['GET','POST'])
def formularioEnvioMensaje():
    obtenerDatos = obtenerVecinos()
    return render_template("enviarMensaje.html",listadoVecinos=obtenerDatos)    

# de flask le enviamos un mensaje a raspberry pi pico
@app.route('/enviarMensaje',methods=['GET','POST'])   
def enviarMensaje():
    
    if request.method == "POST":
        mensaje = request.form.get('txtEnviarMensaje')

        hostEmisor = request.form.get('txtHostEmisor')
        hostReceptor = request.form.get('selectVecinos')
        
        idMensaje = obtenerUltimoIDMensaje()
        idMe = str(idMensaje)
        hasBeenReceived = "0"

        mensajeCompleto = f"{hostEmisor}|{hostReceptor}|{idMe}|{hasBeenReceived}|{mensaje}"

        try:
            if serial_port.is_open:
                

                try:                
                    obtenerFechaHora = datetime.now()

                    formatearFecha = obtenerFechaHora.strftime("%d/%m/%Y %H:%M:%S")

                    conexion = sqlite3.connect(nombreBaseDatos)
                    cursor = conexion.cursor()
                    
                    if mensaje is not None and hostEmisor is not None and hostReceptor is not None:
                        cursor.execute("insert into mensajes(tipoMensaje,mensaje,fecha) values (?,?,?)", ("Enviado",mensajeCompleto,formatearFecha))
                        conexion.commit()
                        serial_port.write(mensajeCompleto.encode('utf-8'))
                    else:
                        formatoJSON = [{'success':False,'mensaje':"Habian valores vacios"}]
                        return jsonify({'data': formatoJSON})


                except Exception as e:
                    print("Se genero el siguiente error: ",e)
                
                formatoJSON = [{'success':True,'mensaje':"enviado"}]
                return jsonify({'data': formatoJSON})

            else:
                print("Estoy en el metodo /enviarMensaje en el else: "  + mensaje)
                formatoJSON = [{'success':False,'mensaje':"Verifica que este habilitado el puerto de serial"}]
                
                return jsonify({'data': formatoJSON})
        except Exception as e:
            formatoJSON = [{'success':False,'mensaje':"exception"}]
            return jsonify({'data': formatoJSON})
            #return jsonify({'success': False, 'mensaje': f'Error al enviar mensaje: {e}'})
    else:
        formatoJSON = [{'success': False, 'mensaje': "Campos requeridos vacíos o nulos"}]
        return jsonify({'data': formatoJSON})
    
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    global reading_thread
    if reading_thread is None or not reading_thread.is_alive():
        reading_thread = threading.Thread(target=leerPuerto)
        reading_thread.start()
    else:
        print('El hilo ya está en ejecución')


if __name__ == '__main__':
    abrirPuerto(PUERTO_DEFAULT)

    #app.run(debug=True, port=5000)
    socketio.run(app, debug=True,port=5000,host='0.0.0.0')