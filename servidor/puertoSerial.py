import serial
import serial.tools.list_ports
import sqlite3
import sys 
from datetime import datetime

from database import nombreBaseDatos

from logger import registroLog
from flask import session
from flask_socketio import SocketIO


'''
Puerto por defecto de la raspberry pi pico en MACOS.
Es posible que el puerto cambie en otros sistemas operativos.

Se utiliza este puerto para hacer la comunicacion del cable usb a serial UART.
De está forma se puede enviar y recibir datos desde el servidor web a la raspberry pi pico
'''
PUERTO_DEFAULT = "/dev/cu.usbserial-0001"

#PUERTO_DEFAULT = "/dev/cu.usbmodem-1201"

valorBaudarate = 9600

serial_port = serial.Serial()

def obtenerPuertosCOM():
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    return com_ports

def abrirPuerto(puerto):
    try:
        if not serial_port.is_open:
            serial_port.port=puerto
            serial_port.baudrate=valorBaudarate
            serial_port.open()
        return True,"Puerto abierto correctamente"
    except Exception as e:
        registroLog.info(f"Error al abrir el puerto: {e}")
        return False,f"Error al abrir el puerto: {e}"

def leerPuerto():
    print("Iniciando hilo de lectura")
    if "usuarioSesion" in session:
        global idUsuarioSes
        idUsuarioSes = session.get("idUsuario")
    
    if serial_port.is_open and serial_port.in_waiting > 0:
        try:
            while True:
                line = serial_port.readline().decode('utf-8')
                
                if not line:
                    print("No hay datos recibidos")
                    break
                
                # el mensaje se envia desde la raspberry pi pico
                mensajeRecibido = str(line)
 
                #print("estoy aqui en mensaje recibido: ",mensajeRecibido)
                obtenerFechaHora = datetime.now()
                formatearFecha = obtenerFechaHora.strftime("%d/%m/%Y %H:%M:%S")
                            
                conexion = sqlite3.connect(nombreBaseDatos)
                cursor = conexion.cursor()  

                if mensajeRecibido.strip() == "INIT":
                    print("Se ha recibido el mensaje INIT")
                    
                    cursor.execute("insert into mensajes(tipoMensaje,mensaje,fecha,idUsuario) values (?, ?, ?,?)", ("Recibido",mensajeRecibido,formatearFecha,idUsuarioSes))
                    cursor.execute("insert into mensajes(tipoMensaje,mensaje,fecha,idUsuario) values (?, ?, ?,?)", ("Enviado","STARTED",formatearFecha,idUsuarioSes))
                    conexion.commit()

                    serial_port.write("STARTED".encode('utf-8'))
                    conexion.close()
                    #socketio.emit('datos_actualizados', {'data': line})
                else:
                    cursor.execute("insert into mensajes(tipoMensaje,mensaje,fecha,idUsuario) values (?, ?, ?,?)", ("Recibido",mensajeRecibido,formatearFecha,idUsuarioSes))
                    conexion.commit()
                    conexion.close()                    

                registroLog.info(f"Se recibio el mensaje: {mensajeRecibido} y se almaceno en la base de datos.")
                
                #socketio.emit('datos_actualizados', {'data': line})
        except sqlite3.Error as e:
            print(f"Error al insertar en la base de datos: {e}")
            registroLog.info("Se produjo un error al querer insertar a la base de datos. El mensaje recibido es: {mensajeEnviar}")
            
        except Exception as e:
            print("Se produjo el siguiente error: ",e)
        #socketio.sleep(1)
    else:
        abrirPuerto(PUERTO_DEFAULT)
        print("El puerto no esta abierto o no hay datos")
            
