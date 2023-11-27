'''
Archivo para configurar el registro de logs de la aplicacion
'''
import logging
nombreLog = "app.log"
# configurar registro de sistema
logging.basicConfig(filename=nombreLog,level=logging.DEBUG)
# realizar el registro de los errores
registroLog = logging.getLogger("index")