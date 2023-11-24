import time
from machine import Pin, UART
from time import sleep

HOSTNAME="santos"

valorBaudarte = 9600
# Ajusta los pines TX y RX según tu configuración
def ConfigurarRaspberryPiPico(id,baudrate,tx,rx):
    return UART(id,baudrate,tx=Pin(tx),rx=Pin(rx))


uart_usb = ConfigurarRaspberryPiPico(0,valorBaudarte,0,1)
uartRaspberry = ConfigurarRaspberryPiPico(1,valorBaudarte,4,5)
mensajeINIT="INIT"
flagSTARTED="STARTED"
simboloOR="|"

# Configura la conexión serial UART para la comunicación entre Raspberry Pi Picos
def enviarMensaje(uart, mensaje):
    uart.write(mensaje+'\n')
    sleep(1)
    #uart.write('\n')

def recibirMensaje(uart):
    if uart.any() > 0:
        
        return uart.read()
    else:
        return None

contador=0
while True:
    contador+=1
    
    mensajeRecibidoServidorWeb = recibirMensaje(uart_usb)
    if mensajeRecibidoServidorWeb:
        decodificarMensajeDesdeServidor = mensajeRecibidoServidorWeb.decode('utf-8')
        if decodificarMensajeDesdeServidor==mensajeINIT:
            print("El servidor web inicio el comando: ",decodificarMensajeDesdeServidor)
            # se envia el mensaje al Raspberry que este conectado a mi controlador (Raspberry)
            enviarMensaje(uartRaspberry ,mensajeINIT)
            print("Se ha enviado el mensaje :",mensajeINIT+ " al Raspberry Pi Pico")
        else:
            mensajeSplit = decodificarMensajeDesdeServidor.split("|")
            longitudMensaje = len(mensajeSplit)
            # debido al formato del mensaje establecido como protocolo: Host emisor|Host receptor|idMensaje|hasBeenReceivedR|mensaje
            # para que me incluya el texto mensaje
            if longitudMensaje>=5:
                hostEmisor=mensajeSplit[0]
                #global HOSTNAME
                
                #HOSTNAME = hostEmisor
                hostReceptor=mensajeSplit[1]
                idMensaje=mensajeSplit[2]
                hasBeenReceived=mensajeSplit[3]
                mensajeCompleto = mensajeSplit[4]
                mensajeCompletoEnviar = hostEmisor+simboloOR+hostReceptor+simboloOR+idMensaje+simboloOR+hasBeenReceived+simboloOR+mensajeCompleto
                
                print("El servidor web envio el siguiente formato de mensaje: ",decodificarMensajeDesdeServidor)
                print("El Raspberry emisor es: ",hostEmisor)
                print("El Raspberry receptor es: ",hostReceptor)
                print("El id del mensaje es: ",idMensaje)
                print("Estado actual del mensaje: ",hasBeenReceived)
                print("El mensaje con el formato del protocolo enviado es: ",mensajeCompletoEnviar)
                enviarMensaje(uartRaspberry,mensajeCompletoEnviar)

    mensajeRecibidoDesdeOtrasRaspberrys = recibirMensaje(uartRaspberry)
    if mensajeRecibidoDesdeOtrasRaspberrys:
        decodificarMensajeDeRasperrys= mensajeRecibidoDesdeOtrasRaspberrys.decode('utf-8')
        print("Se ha recibido el mensaje ",decodificarMensajeDeRasperrys+ " de otra Raspberry")
        if decodificarMensajeDeRasperrys.strip()==mensajeINIT:
            print("Se ha recibido el mensaje ",mensajeINIT+ " de otra Raspberry")
            print("Se envio el mensaje ",flagSTARTED+ " a la otra Raspberry")
            enviarMensaje(uart_usb,flagSTARTED)
            enviarMensaje(uartRaspberry,flagSTARTED)

        elif decodificarMensajeDeRasperrys.strip()==flagSTARTED:
            print("Me han enviado el mensaje:",flagSTARTED + " desde la otra Raspberry")
            print("Enviando formato completo de mensaje: ")
            enviarMensaje(uart_usb,decodificarMensajeDeRasperrys)
            enviarMensaje(uartRaspberry,decodificarMensajeDeRasperrys)
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
                mensajeCompletoEnviar = hostEmisor+simboloOR+hostReceptor+simboloOR+str(idMensaje)+simboloOR+str(confirmarRecepcionMensaje)+simboloOR+mensajeCompleto
                
                
                if hostReceptor== HOSTNAME:
                    print("Mensaje dirigido para mi")
                    print("Mensaje ",decodificarMensajeDeRasperrys + " recibido de Raspberry emisor: "+hostEmisor)
                    print("El Raspberry emisor es: ",hostEmisor)
                    print("El Raspberry receptor es: ",hostReceptor)
                    print("El id del mensaje es: ",idMensaje)
                    print("Estado actual del mensaje: ",hasBeenReceived)
                    print("El mensaje enviado es: ",mensajeCompletoEnviar + ". Actualice el estado de recepcion del mensaje a 1")
                    enviarMensaje(uartRaspberry,mensajeCompletoEnviar)
                    sleep(0.5)
                    enviarMensaje(uart_usb,mensajeCompletoEnviar)
                    sleep(0.5)

                else:
                    print("Mensaje recibido con formato del protocolo: ",decodificarMensajeDeRasperrys)
                    print("El Raspberry receptor: ",hostReceptor+  " no va dirigido para mi ("+HOSTNAME+"). Se reenvio el mensaje porque no es para mi")
                    nuevoMensaje = mensajeCompletoEnviar+"_Reenviado"
                    print("xxxxxxx: ",mensajeCompletoEnviar)
                    #enviarMensaje(uartRaspberry,nuevoMensaje)
                    enviarMensaje(uart_usb,nuevoMensaje)
    #else:
        #print("estoy en el else: ",mensajeRecibidoDesdeOtrasRaspberrys)