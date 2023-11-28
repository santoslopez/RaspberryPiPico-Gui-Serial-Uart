from flask import render_template,redirect,url_for,flash,session,Blueprint
from flask import request
from database import nombreBaseDatos
from functools import wraps


from logger import registroLog
import sqlite3

auth = Blueprint('auth',__name__)



# realizar la consulta de login en sqlite 
def queryLogin(usuario,passwordGuardar):
    conexion = sqlite3.connect(nombreBaseDatos)
    cursor = conexion.cursor()  
    cursor.execute("select * from usuarios where usuario=? and password=?",(usuario,passwordGuardar,))
    ejecutar = cursor.fetchall()
    conexion.close()
    return ejecutar

@auth.route('/login',methods=['POST'])

def login():
    if "usuarioSesion" not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        usuario = request.form.get("txtUsuario")
        passwordGuardar = request.form.get("txtPassword")

        # validar usuario y password por medio de la base de datos sqlite
        #conexion = sqlite3.connect(nombreBaseDatos)
        #cursor = conexion.cursor()
        #cursor.execute("select * from usuarios where usuario=? and password=?",(usuario,passwordGuardar,))
        #ejecutar = cursor.fetchall()
        #conexion.close()
        ejecutar = queryLogin(usuario,passwordGuardar)

        # validar que el usuario y password sean correctos
        if len(ejecutar) > 0:
            # se crea la sesion de que existe el usuario
            session["usuarioSesion"]=usuario
            # se accede al primer resultado y primera columna
            session["idUsuario"]=ejecutar[0][0]
            usuarioSes = session["usuarioSesion"]
            idUsuarioSes = session["idUsuario"]
            flash("Inicio de sesion exitoso", "success")
            return render_template("main/index.html",registroExitoso=True,usuarioSesion=usuarioSes,idUsuario=idUsuarioSes)
        else:
            flash("Usuario o contraseña incorrectos","error")
            return render_template("auth/login.html",registroExitoso=False)

       
@auth.route('/fmrLogin',methods=['GET','POST'])
def frmLogin():
    if "usuarioSesion" in session:
        idUsuarioSes = session["idUsuario"]
        return render_template("main/index.html",idUsuario=idUsuarioSes,usuarioSesion=session["usuarioSesion"])
    else:
        flash("No has iniciado sesión")
        registroLog.info("El usuario no ha iniciado sesion redirigido al login.")
        return render_template("auth/login.html")
    
@auth.route('/frmRegistroCuenta',methods=['GET','POST'])
def frmRegistroCuenta():
    return render_template("auth/frmRegistroCuenta.html")

@auth.route('/registroCuenta',methods=["POST"])
def registroCuenta():
    if request.method == "POST":
        usuarioGuardar = request.form.get("txtUsuario")
        passwordGuardar = request.form.get("txtPassword")
        
        if not usuarioGuardar or not passwordGuardar:
            flash("Debes ingresar un usuario y una contraseña","error")
            return render_template("auth/frmRegistroCuenta.html")
        else:
            with sqlite3.connect(nombreBaseDatos) as conexion:
                cursor = conexion.cursor()
                cursor.execute("INSERT INTO usuarios(usuario,password) VALUES (?, ?)",(usuarioGuardar,passwordGuardar))
                conexion.commit()
                registroLog.info("El usuario se ha guardado correctamente.")

                return render_template("auth/registroExitoso.html")
    else:
        return render_template("auth/frmRegistroCuenta.html")


# cerrar la sesion del usuario
@auth.route('/logout',methods=['GET','POST'])
def logout():
    session.pop("usuarioSesion",None)
    flash("Se ha cerrado la sesion correctamente","sucess")
    return redirect(url_for("auth.frmLogin"))