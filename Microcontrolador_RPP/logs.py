# archivo que permite crear un historial o log de los mensajes enviados y recidos o errores producidos
import time

def crearLogArchivo(archivoTexto,mensaje):
    archivoTexto.write(mensaje)
    # asegurarse que se haya escribido 
    archivoTexto.flush()

# recuperar la fecha y hora actual
def obtenerFechaHoraActual():
    datosFechaHora = time.time()
    datosLocal = time.localtime(datosFechaHora)
    year = "{}/{}/{}".format(datosLocal[2],datosLocal[1],datosLocal[0])
    hora = " Hora: {}:{}:{}".format(datosLocal[3],datosLocal[4],datosLocal[5])
    return year + hora
