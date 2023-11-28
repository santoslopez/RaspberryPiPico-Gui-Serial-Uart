from flask_socketio import SocketIO
from flask import render_template, request

class ErrorHandlers:
    @staticmethod
    def register(app,socketio):
        # manejo de errores 
        @socketio.on_error_default
        def default_error_handler(e):
            print('Error en socketio. El error que se produjo es: ', e)
            #print(request.event["message"])
            #print(request.event["args"])
            #print(e)

        # manejo de error de metodo no permitido
        @app.errorhandler(405)
        def metodoNoPermitido(e):
            return render_template('error/405.html'), 405

        @app.errorhandler(404)
        def recursoNoEncontrado(e):
            return render_template('error/404.html'), 404