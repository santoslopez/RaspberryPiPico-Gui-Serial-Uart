from flask import Blueprint,render_template,request,redirect,url_for,jsonify
import sqlite3


DATABASE = 'database.db'

VecinosView = Blueprint('VecinosView',__name__)

@VecinosView.route('/vecinos')
#@app.route('/vecinos')
def vecinos():
    return render_template('vecinos.html')

@VecinosView.route('/obtenerVecinos')
#@app.route('/obtenerVecinos')
def obtenerVecinos():
    conexion = sqlite3.connect(DATABASE)
    print("Opened database successfully")
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()
    cursor.execute("select * from vecinos")
    vecinos = cursor.fetchall()
    print(vecinos)
    conexion.close()
    
    formatoJSON = [{'id':vecinos['id'],'nombre':vecinos['nombreGrupo']} for vecinos in vecinos]
    # el nombre de data se utiliza en el datatable para recuperar los datos
    return jsonify({'data': formatoJSON})



@VecinosView.route('/registrarVecino',methods=['POST'])
def registrarVecino():
    if request.method == "POST":
        try:
            nombre = request.form.get("txtNombreGrupo")

            # validar que el nombre no esté vacío
            if nombre == "" or nombre is None:
                return redirect(url_for('index'))
            else:
                
                conexion = sqlite3.connect(DATABASE)
                print("Opened database successfully")
                cursor = conexion.cursor()
                cursor.execute("insert into vecinos(nombreGrupo) values(?)",(nombre,))
                conexion.commit()
                conexion.close()
                print("Registro insertado correctamente")
        except Exception as e:
            print("Error en la inserción de datos de vecino")
            print(e)
        finally:
            print("estoy en finally")
            return redirect(url_for('index'))