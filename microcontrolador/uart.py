import time
from machine import Pin, UART
from time import sleep

HOSTNAME = "GP5"

valorBaudarte = 9600

# Ajusta los pines TX y RX según tu configuración
def ConfigurarRaspberryPiPico(id,baudrate,tx,rx):
    return UART(id,baudrate,tx=Pin(tx),rx=Pin(rx))

uart_usb = ConfigurarRaspberryPiPico(0,valorBaudarte,0,1)
uartRaspberry = ConfigurarRaspberryPiPico(1,valorBaudarte,4,5)


mensajeINIT = "INIT"
flagSTARTED = "STARTED"

# Configura la conexión serial UART para la comunicación entre Raspberry Pi Picos
def enviarMensaje(uart, mensaje):
    uart.write(mensaje)
    uart.write('\n')
    sleep(0.5)

def recibirMensaje(uart):
    if uart.any() > 0:
        #print("estoy aquiiii")
        #variable = uart.read()
        
        #print("validando variables: ",variable)
        return uart.read()
    else:
        return None
    
def protocoloMensajesUART(uartRaspberry,uart_usb):
    mensajeDeOtrosRaspberryPiPico = recibirMensaje(uartRaspberry)
    
    if mensajeDeOtrosRaspberryPiPico:
        #print("Me enviaron de otros raspberrys:",mensajeDeOtrosRaspberryPiPico.decode('utf-8')+"\n")
        # mensajeDecodificadoR = mensajeDeOtrosRaspberryPiPico.decode("utf-8")
        mensajeDecodificadoR = mensajeDeOtrosRaspberryPiPico.decode("utf-8")

        print("Mensaje que me enviaron de Raspberry Pi Pico:",mensajeDecodificadoR)
        hostEmisorR=mensajeDecodificadoR[0:3]
        # se obtiene el primer |
        simboloOR1R=mensajeDecodificadoR[3:4]
        hostReceptorR=mensajeDecodificadoR[4:7]
        # se obtiene el segundo |
        simboloOR2R=mensajeDecodificadoR[7:8]
        # idMensaje
        idMensajeR = mensajeDecodificadoR[8:10]
        simboloOR3R = mensajeDecodificadoR[10:11]
        hasBeenReceivedR = mensajeDecodificadoR[11:12]
        simboloR4R= mensajeDecodificadoR[12:13]
        longitudMensajeRecibidoR = len(mensajeDecodificadoR)
        mensajeCompletoR= mensajeDecodificadoR[13:20].strip()
        # utilizo la variable en caso sea necesario enviarlo a alguien mas
        mensajeCompletoReenviar = hostEmisorR+simboloOR1R+hostReceptorR+simboloOR2R+idMensajeR+simboloOR3R+hasBeenReceivedR+simboloR4R+mensajeCompletoR
        
        # valido que el mensaje que me envia es para mi
        
        if hostReceptorR.lower()==HOSTNAME.lower() or hostReceptorR.upper()==HOSTNAME.upper():
            if mensajeCompletoR == mensajeINIT:
                idNuevoConfirmacion = 1
                nuevoMensajeR = hostEmisorR+simboloOR1R+hostReceptorR+simboloOR2R+idMensajeR+simboloOR3R+str(idNuevoConfirmacion)+simboloR4R+"STARTED"
                enviarMensaje(uartRaspberry,nuevoMensajeR)
                enviarMensaje(uart_usb,nuevoMensajeR)
                print("Inicie el comando para conectarme con el host receptor: ",hostReceptorR)
            elif ((mensajeCompletoR.upper() == flagSTARTED.upper()) or (mensajeCompletoR.lower() == flagSTARTED.lower())):
                idNuevoConfirmacion = 1
                nuevoMensajeR = hostEmisorR+simboloOR1R+hostReceptorR+simboloOR2R+idMensajeR+simboloOR3R+str(idNuevoConfirmacion)+simboloR4R+"CONECTADO"
                enviarMensaje(uart_usb,nuevoMensajeR)
                enviarMensaje(uartRaspberry,nuevoMensajeR)
                print("Estoy conectado con el host receptor: ",hostEmisorR)
            else:
                idNuevoConfirmacion = 0
                print("Comando de mensaje no detectado: "+mensajeCompletoR + ". El mensaje completo es: "+mensajeCompletoReenviar+". Se envio nuevamente")
                enviarMensaje(uart_usb,mensajeCompletoReenviar)
                enviarMensaje(uartRaspberry,mensajeCompletoReenviar)
        else:
            print("No se realizo nada porque no hay datos en la raspberry.")
            #enviarMensaje(uartRaspberry,mensajeCompletoReenviar)
            #enviarMensaje(uart_usb,mensajeCompletoReenviar)
            


while True:
    # Esperar mensaje desde el servidor web (convertidor USB a serial)
    mensajeMiServidorWeb = recibirMensaje(uart_usb)
    if mensajeMiServidorWeb:
        print("Mensaje recibido desde el servidor web:",mensajeMiServidorWeb.decode('utf-8'))
        
        mensajeRecibidoDecodificado = mensajeMiServidorWeb.decode('utf-8')


        hostEmisor = mensajeRecibidoDecodificado[0:3]
        # se obtiene el primer |
        simboloOR1 = mensajeRecibidoDecodificado[3:4]
        hostReceptor = mensajeRecibidoDecodificado[4:7]
        # se obtiene el segundo |
        simboloOR2 = mensajeRecibidoDecodificado[7:8]
        # idMensaje
        idMensaje = mensajeRecibidoDecodificado[8:10]
        simboloOR3 = mensajeRecibidoDecodificado[10:11]
        hasBeenReceived = mensajeRecibidoDecodificado[11:12]
        simboloOR4 = mensajeRecibidoDecodificado[12:13]
        longitudMensajeRecibido = len(mensajeRecibidoDecodificado)
        mensajeCompleto = mensajeRecibidoDecodificado[13:longitudMensajeRecibido].strip()
        longitudMensajeRecibido = len(mensajeRecibidoDecodificado)
            
        
        nuevoMensaje = hostEmisor+simboloOR1+hostReceptor+simboloOR2+idMensaje+simboloOR3+hasBeenReceived+simboloOR4+mensajeCompleto
        print("Mensaje del servidor web: ",nuevoMensaje)          
    
        # verificar que el mensaje que recibi tiene como destinatario a mi hostname
        if hostEmisor.lower()==HOSTNAME or hostEmisor.upper()==HOSTNAME:
            print("Yo envie el mensaje desde mi formulario ahora lo voy a enviar",hostReceptor)
                                
            #nuevoFormatoMensaje = hostEmisor+simboloOR1+hostReceptor+simboloOR2+idMensaje+simboloOR3+hasBeenReceived+simboloOR4+mensajeSTARTED
            if mensajeCompleto==mensajeINIT:
                
                print("Acabo de enviar el mensaje a :",hostReceptor)
                enviarMensaje(uart_usb,nuevoMensaje)
                enviarMensaje(uartRaspberry,nuevoMensaje)            
            elif mensajeCompleto==flagSTARTED:
                
                #print("E:",hostReceptor)
                print("Se envio el mensaje: ",nuevoMensaje + " desde el servidor web a la raspberry pi pico")
                #enviarMensaje(uart_usb,nuevoMensaje)

                enviarMensaje(uartRaspberry,nuevoMensaje)
            else:
                print("El comando del mensaje no se detecto sin embargo se envio el mensaje")
                #enviarMensaje(uart_usb,nuevoMensaje)

                enviarMensaje(uartRaspberry,nuevoMensaje)
    # aqui mandar a llamar al metodo
    protocoloMensajesUART(uartRaspberry,uart_usb)