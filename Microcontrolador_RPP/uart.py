import time
from machine import Pin, UART
from time import sleep

HOSTNAME = "santos"

valorBaudarte = 9600
# Ajusta los pines TX y RX según tu configuración
def ConfigurarRaspberryPiPico(id,baudrate,tx,rx):
    return UART(id,baudrate,tx=Pin(tx),rx=Pin(rx))


uart_usb = ConfigurarRaspberryPiPico(0,valorBaudarte,0,1)
uartRaspberry = ConfigurarRaspberryPiPico(1,valorBaudarte,4,5)
mensajeINIT="INIT"
flagSTARTED="STARTED"
flagCONECTADOS="CONECTADOS"
simboloOR="|"

# Configura la conexión serial UART para la comunicación entre Raspberry Pi Picos
def enviarMensaje(uart, mensaje):
    uart.write(mensaje+'\n')
    sleep(3)
    #uart.write('\n')

def recibirMensaje(uart):
    sleep(3)
    if uart.any() > 0:
        # limpiar el buffer
        #uart.read()
        return uart.read()
    else:
        return None


while True:

    mensajeRecibidoServidorWeb = recibirMensaje(uart_usb)
    if mensajeRecibidoServidorWeb:
        
        decodificarMensajeDesdeServidor = mensajeRecibidoServidorWeb.decode('utf-8')

        mensajeSplit = decodificarMensajeDesdeServidor.split("|")

        longitudMensaje = len(mensajeSplit)
        # debido al formato del mensaje establecido como protocolo: Host emisor|Host receptor|idMensaje|hasBeenReceivedR|mensaje
        # para que me incluya el texto mensaje
        
        if longitudMensaje>=5:
            hostEmisor=mensajeSplit[0]
            HOSTNAME = hostEmisor
                
            hostReceptor=mensajeSplit[1]
            idMensaje=mensajeSplit[2]
            hasBeenReceived=mensajeSplit[3]
            mensajeCompleto = mensajeSplit[4]
            mensajeCompletoEnviar = hostEmisor+simboloOR+hostReceptor+simboloOR+idMensaje+simboloOR+hasBeenReceived+simboloOR+mensajeCompleto
                
            print("El servidor web envio el siguiente formato de mensaje: ",decodificarMensajeDesdeServidor)
            print("Raspberry emisor es: ",hostEmisor)
            print("Raspberry receptor es: ",hostReceptor)
            print("El id del mensaje: ",idMensaje)
            print("Estado actual del mensaje: ",hasBeenReceived)
            print("El mensaje enviado es: ",mensajeCompleto)
            enviarMensaje(uartRaspberry,mensajeCompletoEnviar)
        elif longitudMensaje==2:
            print("Formato original del mensaje inicial enviado desde el servidor: ",mensajeSplit)

            hostEmisor=mensajeSplit[0]
            HOSTNAME = hostEmisor
                
            mensajeInicialServidor=mensajeSplit[1]
                
            if mensajeInicialServidor==mensajeINIT:
                print("El servidor web inicio el comando: ",mensajeInicialServidor)    
                print("El Raspberry emisor es: ",hostEmisor)
                   
                # se envia el mensaje al Raspberry que este conectado a mi controlador (Raspberry)
                enviarMensaje(uartRaspberry,mensajeINIT)
                print("Se ha enviado el mensaje :",mensajeINIT+ " al Raspberry Pi Pico")
               
            else:
                print("Formato no admitido")

    mensajeRecibidoDesdeOtrasRaspberrys = recibirMensaje(uartRaspberry)
 
    if mensajeRecibidoDesdeOtrasRaspberrys:
        decodificarMensajeDeRasperrys = mensajeRecibidoDesdeOtrasRaspberrys.decode('utf-8')
        if decodificarMensajeDeRasperrys==mensajeINIT:
            print("Se ha recibido el mensaje ",mensajeINIT+ " de otra Raspberry")
            print("Se envio el mensaje ",flagSTARTED+ " a la otra Raspberry")
            enviarMensaje(uart_usb,flagSTARTED)
            enviarMensaje(uartRaspberry,flagSTARTED)

        elif decodificarMensajeDeRasperrys==flagSTARTED:
            print("Me han enviado el mensaje: ",flagSTARTED + " desde la otra Raspberry")
            print("Enviando formato completo de mensaje: ")
            #enviarMensaje(uart_usb,decodificarMensajeDeRasperrys)
            enviarMensaje(uartRaspberry,flagCONECTADOS)
        else:
            mensajeSplit = decodificarMensajeDeRasperrys.split("|")
            longitudMensaje = len(mensajeSplit)
            # debido al formato del mensaje establecido como protocolo: Host emisor|Host receptor|idMensaje|hasBeenReceivedR|mensaje
            # para que me incluya el texto mensaje
            if longitudMensaje>=5:
                hostEmisor=mensajeSplit[0]
                hostReceptor=mensajeSplit[1]
                
                idMensaje=mensajeSplit[2]
                hasBeenReceived=mensajeSplit[3]
                mensajeCompleto = mensajeSplit[4]
                
                confirmarRecepcionMensaje = 1
                mensajeCompletoEnviar = hostEmisor+simboloOR+hostReceptor+simboloOR+idMensaje+simboloOR+confirmarRecepcionMensaje+simboloOR+mensajeCompleto
                
                
                if hostReceptor== HOSTNAME:
                    print("Mensaje recibido desde otra Raspberry: ",decodificarMensajeDeRasperrys)
                    print("Raspberry emisor es: ",hostEmisor)
                    print("Raspberry receptor es: ",hostReceptor)
                    print("El id del mensaje es: ",idMensaje)
                    print("Estado actual del mensaje: ",hasBeenReceived)
                    print("El mensaje enviado es: ",mensajeCompleto)
                    enviarMensaje(uartRaspberry,mensajeCompletoEnviar)
                    enviarMensaje(uart_usb,mensajeCompletoEnviar)

                else:
                    print("El Raspberry receptor: ",hostReceptor+  " no va dirigido para mi ("+HOSTNAME+")")
                    print("Renviando mensaje debido que no va dirigido para mi")
                    enviarMensaje(uartRaspberry,mensajeCompletoEnviar+"Reenviado")
                    enviarMensaje(uart_usb,mensajeCompletoEnviar+"Reenviado")

