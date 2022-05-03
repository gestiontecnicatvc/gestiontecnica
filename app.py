from genericpath import exists
from turtle import ycor
from xml.dom.minidom import Element
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2 
import psycopg2.extras
from datetime import datetime
from datetime import time
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
from config import config
from models.ModelUser import ModelUser
from models.entities.User import User
import urllib.request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__) 
app.secret_key = "*tvc_digit_2022"
#app.config["SECURITY_CSRF_COOKIE_NAME"] = "XSRF-TOKEN"
#app.config["WTF_CSRF_TIME_LIMIT"] = None
#app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

csrf = CSRFProtect()
login_manager_app = LoginManager(app)

'''DB_HOST = "ec2-54-156-110-139.compute-1.amazonaws.com"
DB_NAME = "d735ss5eugodet"
DB_USER = "gcjwfpjpgpbjso"
DB_PASS = "563d04c0c5826ad5ec8f27b91969f8d2375aae7d0f72b8119f23273985b99547"
PORT = 5432'''

DB_HOST = "127.0.0.1"
DB_NAME = "gestion_tecnica"
DB_USER = "postgres"
DB_PASS = "gestion2022"
#DB_PASS = "12345678"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) 
#conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=PORT) 

@app.route('/')
def index():
    #return render_template('select.html')
    return redirect(url_for('login'))

@app.route('/tecnicos')
def tecnicos():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT te_identificacion FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        
        tecn = []
        for y in range(0,1):
            for f in tec:
               tecn.append(str(f).replace("'","").replace("[","").replace("]",""))        

        tecnicos = str(tecn).replace("'","")
        return render_template('tecnicos2.html', tecnicos = tecnicos, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_tecnico', methods=['POST'])
def add_tecnico():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        id = request.form['id']
        ident = int(id)
        cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (str(ident),) )
        data = cur.fetchall()
        cur.close()
        
        if data:
            return redirect(url_for('tecnicos'))
        else:
            if request.method == 'POST':
                id = request.form['id']
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                telefono = request.form['telefono']
                direccion = request.form['direccion']
                email = request.form['email']
                tipo = request.form['tipo']
                nivel = request.form['nivel']
                fech = str(datetime.today().strftime('%d-%m-%Y'))
                fecha = fech[:10]        
                #GUARDAR FOTO
                ##foto = request.files['foto']
                #name = secure_filename(foto.filename)
                ##foto.save(os.path.join(app.config['UPLOAD_FOLDER'], id+".jpg"))
                
                #cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                #cur.execute("INSERT INTO tecnicos (te_identificacion, te_nombres, te_apellidos, te_telefono, te_direccion, te_email, te_tipo, te_nivel, te_fechaingreso, te_fechasalida, te_estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (str(id), nombres, apellidos, telefono, direccion, email, tipo, nivel, fecha, fecha, True))
                #conn.commit()
                #cur.close()
                
                return redirect(url_for('tecnicos'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_tecnicos_activos')
def listado_tecnicos_activos():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM tecnicos WHERE te_estado = True"
        cur.execute(s) # Execute the SQL
        tecnicos = cur.fetchall()
        cur.close()
        return render_template('listado_tecnicos_activos.html',tecnicos = tecnicos, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_tecnicos_inactivos')
def listado_tecnicos_inactivos():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT te_nombres, te_apellidos, te_tipo, te_nivel, te_identificacion FROM tecnicos WHERE te_estado = False"
        cur.execute(s) # Execute the SQL
        tecnicos = cur.fetchall()
        cur.close()
        return render_template('listado_tecnicos_inactivos.html',tecnicos = tecnicos, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'


@app.route('/ver_tecnico/<id>', methods = ['POST', 'GET'])
def see_tecnico(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (id,) )
        data = cur.fetchall()
        cur.close()
        foto = "img/" + id + ".jpg"
        foto_buscar = id + ".jpg"
        directorio = 'static/img/'
        with os.scandir(directorio) as ficheros:
            for fichero in ficheros:
                if fichero.name == foto_buscar:
                    foto = "img/" + id + ".jpg"
                    break
                else:
                    foto = "img/default.jpg"

        return render_template('ver_tecnico.html', tecnico = data[0], user = usu, foto = foto)
    else:
        return 'No tiene permiso de acceso a esa ruta.'


@app.route('/herramientas')
def herramientas():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT he_codigo FROM herramientas"
        cur.execute(s) # Execute the SQL
        her = cur.fetchall()
        cur.close()
        
        herra = []
        for y in range(0,1):
            for f in her:
               herra.append(str(f).replace("'","").replace("[","").replace("]",""))        

        herramientas = str(herra).replace("'","")

        return render_template('herramientas.html', herramientas = herramientas, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_herramientas')
def listado_herramientas():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT he_codigo, he_descripcion,cant_inventario,COALESCE(cant_asignada,0),COALESCE(cant_inventario,0) - COALESCE(cant_asignada,0) FROM (SELECT he_codigo,he_descripcion,he_estado, SUM(he_cantidad) As cant_inventario FROM herramientas GROUP BY he_codigo,he_descripcion,he_estado) As tabla_1 LEFT JOIN (SELECT ah_codherr, SUM(ah_cantidad) As cant_asignada FROM asignacion_herramienta GROUP BY ah_codherr) As tabla_2 ON tabla_2.ah_codherr = tabla_1.he_codigo"
        cur.execute(s) # Execute the SQL
        herramientas = cur.fetchall()
        cur.close()

        return render_template('listado_herramientas.html',herramientas = herramientas,  user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'


@app.route('/add_herramienta', methods=['POST'])
def add_herramienta():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        codigo = request.form['cod']
        descripcion = request.form['desc']
        cantidad = request.form['cant']

        if codigo == "" or descripcion == "" or cantidad == "":
            
            return redirect(url_for('zonas'))
        else:    
            if request.method == 'POST':
                codigo = request.form['cod']
                descripcion = request.form['desc']
                cantidad = request.form['cant']
                estado = request.form['estado']
                cur.execute("INSERT INTO herramientas (he_codigo,he_descripcion,he_cantidad,he_estado,he_disponible) VALUES (%s,%s,%s,%s,%s)", (codigo,descripcion,cantidad,estado,True))
                conn.commit()
                cur.close()
                
                return redirect(url_for('herramientas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/asignar_herramienta')
def asignar_herramienta():
    if 'usuario' in session and session['usuario'] == "admin":
        
        ####TECNICOS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        tecnicos = []
        for y in range(0,1):
            for t in tec:
                tecnicos.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        #### HERRAMIENTAS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c = "SELECT he_descripcion FROM herramientas"
        cur.execute(c) # Execute the SQL
        herr = cur.fetchall()
        cur.close()
        herramientas = []
        for y in range(0,1):
            for t in herr:
                herramientas.append(str(t).replace("'","").replace(",","").replace("[","").replace("]",""))

        return render_template('asignar_herramienta.html', user = usu, tecnicos = tecnicos, herramientas = herramientas)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_ah')
def listado_ah():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos),he_descripcion,ah_cantidad FROM tecnicos INNER JOIN asignacion_herramienta ON tecnicos.te_identificacion = asignacion_herramienta.ah_idtec INNER JOIN herramientas ON herramientas.he_codigo = asignacion_herramienta.ah_codherr GROUP BY te_nombres,te_apellidos,he_descripcion,ah_cantidad"
        cur.execute(s) # Execute the SQL
        asignaciones = cur.fetchall()
        cur.close()
        return render_template('listado_ah.html', user = usu, asignaciones = asignaciones)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_asignacion_herramienta', methods=['POST'])
def add_asignacion_herramienta():
    if 'usuario' in session and session['usuario'] == "admin":
        cantidad = request.form['cant']
        
        if cantidad == "":
            
            return redirect(url_for('asignar_herramienta'))
        else:
            if request.method == 'POST':
                idte = request.form['idtec']
                codher = request.form['codherr']
                cantidad = request.form['cant']
                
                fech = str(datetime.today().strftime('%d-%m-%Y'))
                fecha = fech[:10]

                ##### CODIGO HERRAMIENTA
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT he_codigo FROM herramientas WHERE he_descripcion = %s''' 
                cur.execute(query,(codher,))
                cm = cur.fetchall()
                cur.close() 
                codherr = str(cm).replace("[","").replace("]","").replace(",","").replace("'","")

                #CEDULA TECNICO
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ',te_apellidos) = %s''' 
                cur.execute(query,(idte,))
                tecnico = cur.fetchall()
                cur.close() 
                idtec = str(tecnico).replace("[","").replace("]","").replace(",","").replace("'","")
                
                #### HERRAMIENTAS
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                c = "SELECT he_cantidad FROM herramientas WHERE he_descripcion = %s"
                cur.execute(c,(codher,)) # Execute the SQL
                cant_herr = cur.fetchall()
                cur.close()
                c_herr = str(cant_herr).replace("[","").replace("]","").replace("'","")

                if int(cantidad) <= 0:
                    return redirect(url_for('asignar_herramienta'))    
                else: 
                    if int(cantidad) > int(c_herr):
                       
                        return redirect(url_for('asignar_herramienta'))    
                    else:
                        #cant_nueva = int(c_herr) - int(cantidad)
    
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute("INSERT INTO asignacion_herramienta (ah_idtec,ah_codherr,ah_cantidad,ah_fecha) VALUES (%s,%s,%s,%s)", (idtec,codherr,cantidad,fecha))
                        conn.commit()
                        cur.close()
        
                        #cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        #cur.execute("""
                        #    UPDATE herramientas
                        #    SET he_cantidad = %s
                        #    WHERE he_codigo = %s
                        #""",(cant_nueva, codherr))
                        #conn.commit()
                        #cur.close()

                        return redirect(url_for('asignar_herramienta'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/historial_ah')
def historial_ah():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos),he_descripcion,ah_cantidad,ah_fecha FROM tecnicos INNER JOIN asignacion_herramienta ON tecnicos.te_identificacion = asignacion_herramienta.ah_idtec INNER JOIN herramientas ON herramientas.he_codigo = asignacion_herramienta.ah_codherr GROUP BY te_nombres,te_apellidos,he_descripcion,ah_cantidad,ah_fecha"
        cur.execute(s)
        asignaciones = cur.fetchall()
        cur.close()
        return render_template('historial_ah.html',asignaciones = asignaciones, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/zonas')
def zonas():
    if 'usuario' in session and session['usuario'] == "admin":
        ######## ZONAS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT zo_nombre FROM zonas"
        cur.execute(s) 
        z = cur.fetchall()
        cur.close()
        zonas = []
        for y in range(0,1):
            for f in z:
               zonas.append(str(f).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        return render_template('zonas.html',zonas = zonas ,user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_zona', methods=['POST'])
def add_zona():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        zona = request.form['zona']

        if zona == "":
            return redirect(url_for('zonas'))
        else:    
            if request.method == 'POST':
                zona = request.form['zona']
                cur.execute("INSERT INTO zonas (zo_nombre, zo_estado) VALUES (%s,%s)", (zona,True))
                conn.commit()
                cur.close()
            
                return redirect(url_for('zonas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/notas_tecnicos',methods=["GET","POST"])
def notas_tecnicos():   
    if 'usuario' in session and session['usuario'] == "admin":
        
        ######## ORDENES DE SERVICIO
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT DISTINCT(no_numord) FROM notas"
        cur.execute(s) 
        notas = cur.fetchall()
        cur.close()
        orden = []
        for y in range(0,1):
            for t in notas:
               orden.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        if request.args.get('orden') == None:
            ord = ""
            tecnico = ""
        else:
            ### ID PARA CONSULTAR STOCK
            ord = request.args.get('orden')

        ##### NOTAS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT no_notas,no_fecha,no_estado FROM notas INNER JOIN tecnicos ON notas.no_idtecnico = tecnicos.te_identificacion WHERE no_numord = %s GROUP BY no_numord,te_nombres,te_apellidos,no_fecha,no_estado,no_notas,no_fecha"
        #SELECT no_numord,CONCAT(te_nombres,' ',te_apellidos),no_notas,CONCAT(gz_descmaterial,'=',gz_cantidad),no_fecha,no_estado FROM notas INNER JOIN tecnicos ON notas.no_idtecnico = tecnicos.te_identificacion INNER JOIN gastos_zona ON gastos_zona.gz_numorden = notas.no_numord WHERE no_numord = %s GROUP BY no_numord,te_nombres,te_apellidos,no_notas,no_fecha,no_estado,gz_descmaterial,gz_cantidad"
        #SELECT DISTINCT CONCAT(gz_descmaterial,'=',gz_cantidad),no_numord,CONCAT(te_nombres,' ',te_apellidos),no_fecha,no_estado FROM notas INNER JOIN tecnicos ON notas.no_idtecnico = tecnicos.te_identificacion INNER JOIN gastos_zona ON gastos_zona.gz_numorden = notas.no_numord GROUP BY no_numord,te_nombres,te_apellidos,no_notas,no_fecha,no_estado,gz_descmaterial,gz_cantidad
        cur.execute(s,(ord,))
        notas = cur.fetchall()
        cur.close() 

        ####TECNICO
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        k = "SELECT DISTINCT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos INNER JOIN notas ON notas.no_idtecnico = tecnicos.te_identificacion WHERE no_numord = %s GROUP BY no_numord,te_nombres,te_apellidos" 
        cur.execute(k,(ord,))
        tec = cur.fetchall()
        cur.close() 
        tecnico = (str(tec).replace("'","").replace("[","").replace("]",""))
        
        ##### GASTOS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        f = "SELECT gz_descmaterial, gz_cantidad FROM gastos_zona WHERE gz_numorden = %s"
        cur.execute(f,(ord,))
        gastos = cur.fetchall()
        cur.close() 

        return render_template('notas_tecnicos.html', notas = notas, orden = orden , tecnico = tecnico , orden_servicio = ord , gastos = gastos ,user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/tareas')
def tareas():   
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT COUNT(*) FROM asignacion_tarea"
        cur.execute(s) # Execute the SQL
        reg_os = cur.fetchall()
        cur.close()
        valor_reg = str(tuple(reg_os)).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","")
        auto_incre = int(valor_reg)
        auto_incre = auto_incre + 1

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        tecnicos = []
        for p in range(0,1):
            for r in tec:
                tecnicos.append(str(r).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT zo_nombre FROM zonas"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        zonas = []
        for y in range(0,1):
            for t in tec:
                zonas.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))    

        fech = str(datetime.today().strftime('%d-%m-%Y'))
        fecha = fech[:10]
        
        return render_template('tareas2.html', tecnicos = tecnicos, asignaciones = tareas, zonas = zonas, auto_incre = auto_incre, fecha = fecha, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/tareas_pendientes')
def tareas_pendientes():   
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT at_numsolicitud,CONCAT(te_nombres,' ',te_apellidos),at_zona,at_tipo,at_red,at_usuario,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha FROM asignacion_tarea INNER JOIN tecnicos ON asignacion_tarea.at_idtecnico = tecnicos.te_identificacion WHERE at_estado = 'Pendiente' GROUP BY at_idtecnico,at_numsolicitud,te_nombres,te_apellidos,at_zona,at_tipo,at_red,at_usuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha"
        cur.execute(s)
        pendientes = cur.fetchall()
        cur.close()
        return render_template('tareas_pendientes.html', pendientes = pendientes, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_tareas')
def listado_tareas():   
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT at_numsolicitud,CONCAT(te_nombres,' ',te_apellidos),at_zona,at_tipo,at_red,at_usuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha FROM asignacion_tarea INNER JOIN tecnicos ON asignacion_tarea.at_idtecnico = tecnicos.te_identificacion GROUP BY at_idtecnico,at_numsolicitud,te_nombres,te_apellidos,at_zona,at_tipo,at_red,at_usuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha"
        cur.execute(s)
        tareas = cur.fetchall()
        cur.close()

        return render_template('listado_tareas.html', tareas = tareas, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/historial_tareas')
def historial_tareas():   
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT at_numsolicitud,CONCAT(te_nombres,' ',te_apellidos),at_zona,at_red,at_usuario,at_docusuario,at_detalle,no_notas,at_fecha FROM asignacion_tarea INNER JOIN tecnicos ON asignacion_tarea.at_idtecnico = tecnicos.te_identificacion INNER JOIN notas ON notas.no_numord = asignacion_tarea.at_numsolicitud WHERE at_tipo = 'Mantenimiento' GROUP BY at_idtecnico,at_numsolicitud,te_nombres,te_apellidos,at_zona,at_red,at_usuario,at_docusuario,at_detalle,no_notas,at_fecha"
        cur.execute(s)
        tareas = cur.fetchall()
        cur.close()

        return render_template('historial_tareas.html', tareas = tareas, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/ver_tareas')
def ver_tareas():
    if 'usuario' in session:
        global idtec,asignaciones,horarios
        hora89 = ""
        hora810 = ""
        hora811 = ""
        hora812 = ""
        hora813 = ""
        hora814 = ""
        hora815 = ""
        hora816 = ""
        hora817 = ""
        alertaReloj = ""
        alertaReloj2 = ""
        expirado89 = ""
        expirado810 = ""
        expirado811 = ""
        expirado812 = ""
        expirado813 = ""
        expirado814 = ""
        expirado815 = ""
        expirado816 = ""
        expirado817 = ""
        orden_actividad = ""
        tec = full_name

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
        cur.execute(query,(tec,) )
        data = cur.fetchall()
        cur.close() 
        cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT at_horario FROM asignacion_tarea WHERE at_idtecnico = %s"
        cur.execute(query,(cedula,))
        hora = cur.fetchall()
        cur.close() 

        horarios = []
        for y in range(0,1):
            for t in hora:
                horarios.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        idtec = cedula
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT at_numsolicitud,CONCAT(te_nombres,' ',te_apellidos),at_zona,at_tipo,UPPER(at_red),at_usuario,at_docusuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha FROM asignacion_tarea INNER JOIN tecnicos ON asignacion_tarea.at_idtecnico = tecnicos.te_identificacion WHERE at_idtecnico = %s GROUP BY at_idtecnico,at_numsolicitud,te_nombres,te_apellidos,at_zona,at_tipo,at_red,at_usuario,at_docusuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha"
        cur.execute(s,(idtec,))
        asignaciones = cur.fetchall()
        cur.close() 
        
        formato = "%H:%M:%S"        
        h_actual = datetime.strptime(str(datetime.today().strftime('%H:%M:%S')), formato)
        
        for item in horarios:
            #HORARIO 8 HASTA 17
            h_alerta = datetime.strptime('00:30:00', formato)

            if item == '8 - 9':
                h_ini89 = datetime.strptime('09:00:00', formato)
                if h_actual > h_ini89 :
                    expirado89 = 1
                    alertaReloj = 1
                    hora89 = h_actual - h_ini89
                    orden_actividad = 1
                else:
                    expirado89 = 0
                    hora89 = h_ini89 - h_actual    
                    if str(hora89) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 1

            if item == '8 - 10' or item == '9 - 10':
                h_ini810 = datetime.strptime('10:00:00', formato)
                if h_actual > h_ini810 :
                    expirado810 = 1
                    alertaReloj = 1
                    hora810 = h_actual - h_ini810
                    orden_actividad = 2
                else:
                    expirado810 = 0
                    hora810 = h_ini810 - h_actual    
                    if str(hora810) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 2

            if item == '8 - 11' or item == '9 - 11' or item == '10 - 11':
                h_ini811 = datetime.strptime('11:00:00', formato)
                if h_actual > h_ini811 :
                    expirado811 = 1
                    alertaReloj = 1
                    hora811 = h_actual - h_ini811
                    orden_actividad = 3
                else:
                    expirado811 = 0
                    hora811 = h_ini811 - h_actual
                    if str(hora811) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 3

            if item == '8 - 12' or item == '9 - 12' or item == '10 - 12' or item == '11 - 12':
                h_ini812 = datetime.strptime('12:00:00', formato)
                if h_actual > h_ini812 :
                    expirado812 = 1
                    alertaReloj2 = 1
                    hora812 = h_actual - h_ini812
                    orden_actividad = 4
                else:
                    expirado812 = 0
                    hora812 = h_ini812 - h_actual
                    if str(hora812) <= str(h_alerta):
                        alertaReloj2 = 1
                        orden_actividad = 4

            if item == '8 - 13' or item == '9 - 13' or item == '10 - 13' or item == '11 - 13' or item == '12 - 13':
                h_ini813 = datetime.strptime('13:00:00', formato)
                if h_actual > h_ini813 :
                    expirado813 = 1
                    alertaReloj = 1
                    hora813 = h_actual - h_ini813
                    orden_actividad = 5
                else:
                    expirado813 = 0
                    hora813 = h_ini813 - h_actual
                    if str(hora813) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 5

            if item == '8 - 14' or item == '9 - 14' or item == '10 - 14' or item == '11 - 14' or item == '12 - 14' or item == '13 - 14':
                h_ini814 = datetime.strptime('14:00:00', formato)
                if h_actual > h_ini814 :
                    expirado814 = 1
                    alertaReloj = 1
                    hora814 = h_actual - h_ini814
                    orden_actividad = 6
                else:
                    expirado814 = 0
                    hora814 = h_ini814 - h_actual
                    if str(hora814) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 6                   
            
            if item == '8 - 15' or item == '9 - 15' or item == '10 - 15' or item == '11 - 15' or item == '12 - 15' or item == '13 - 15' or item == '14 - 15':
                h_ini815 = datetime.strptime('15:00:00', formato)
                if h_actual > h_ini815 :
                    expirado815 = 1
                    alertaReloj = 1
                    hora815 = h_actual - h_ini815
                    orden_actividad = 7
                else:
                    expirado815 = 0
                    hora815 = h_ini815 - h_actual                    
                    if str(hora815) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 7

            if item == '8 - 16' or item == '9 - 16' or item == '10 - 16' or item == '11 - 16' or item == '12 - 16' or item == '13 - 16' or item == '14 - 16' or item == '15 - 16':
                h_ini816 = datetime.strptime('16:00:00', formato)
                if h_actual > h_ini816 :
                    expirado816 = 1
                    alertaReloj = 1
                    hora816 = h_actual - h_ini816
                    orden_actividad = 8
                else:
                    expirado816 = 0
                    hora816 = h_ini816 - h_actual                    
                    if str(hora816) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 8

            if item == '8 - 17' or item == '9 - 17' or item == '10 - 17' or item == '11 - 17' or item == '12 - 17' or item == '13 - 17' or item == '14 - 17' or item == '15 - 17' or item == '16 - 17':
                h_ini817 = datetime.strptime('17:00:00', formato)
                if h_actual > h_ini817 :
                    expirado817 = 1
                    alertaReloj = 1
                    hora817 = h_actual - h_ini817
                    orden_actividad = 9
                else:
                    expirado817 = 0
                    hora817 = h_ini817 - h_actual                                        
                    if str(hora817) <= str(h_alerta):
                        alertaReloj = 1
                        orden_actividad = 9
                        
        return render_template('ver_tareas.html', asignaciones = asignaciones, fullname = full_name, user = usu, 
        hora89 = hora89, expirado89 = expirado89, hora810 = hora810, expirado810 = expirado810,
        hora811 = hora811, expirado811 = expirado811, hora812 = hora812, expirado812 = expirado812,
        hora813 = hora813, expirado813 = expirado813, hora814 = hora814, expirado814 = expirado814,
        hora815 = hora815, expirado815 = expirado815, hora816 = hora816, expirado816 = expirado816,
        hora817 = hora817, expirado817 = expirado817, alertaReloj = alertaReloj, alertaReloj2 = alertaReloj2, orden_actividad = orden_actividad)

    else:
        return 'No tiene permiso de acceso a esa ruta.'    
       
@app.route('/add_tareas', methods=['POST'])
def add_tareas():
    if 'usuario' in session and session['usuario'] == "admin":
        
        fech = str(datetime.today().strftime('%d-%m-%Y %H:%M'))
        fecha = fech[:10]

        tec = request.form['idtec']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
        cur.execute(query,(tec,) )
        data = cur.fetchall()
        cur.close() 
        cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")
        
        if request.method == 'POST':
            numsol = request.form['numsol']
            zona = request.form['zona']
            tipo = request.form['tipo']
            red = request.form['red']
            usuario = request.form['usuario']
            direccion = request.form['direccion']
            detalle = request.form['detalles']
            observ = request.form['observaciones']
            de = request.form['de']
            a = request.form['a']
            horario = de + " - " + a
            fecha = datetime.today()

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("INSERT INTO asignacion_tarea (at_numsolicitud, at_idtecnico, at_zona, at_tipo, at_red, at_usuario, at_direccion, at_detalle, at_horario, at_observ_orden, at_estado, at_fecha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (numsol,cedula,zona,tipo,red,usuario,direccion,detalle,horario,observ,'Pendiente',fecha))
            conn.commit()
            cur.close()
            return redirect(url_for('tareas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/notas')
def notas():   
    if 'usuario' in session :
        orden = request.args.get('orden')
        zona = request.args.get('zona')
        nretra = request.args.get('nr')
        tipo = request.args.get('tipo')
        nr = int(nretra)
        
        fech = str(datetime.today().strftime('%d-%m-%Y %H:%M'))
        fecha = fech[:10]
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c = "SELECT ma_descripcion FROM material"
        cur.execute(c) # Execute the SQL
        desc = cur.fetchall()
        cur.close()
        material = []
        for y in range(0,1):
            for t in desc:
                material.append(str(t).replace("'","").replace(",","").replace("[","").replace("]",""))                

        return render_template('notas.html', fecha = fecha, orden = orden, zona = zona, nr = nr, tipo = tipo, material = material ,user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_notas',  methods=['POST'])
def add_notas():  
    if 'usuario' in session: 
        puntaje = 0

        notcierre = request.form['notcierre']
        cantidad = request.form['dat[]']
        if notcierre == "" or cantidad =="":
            
            return redirect(url_for('notas'))
        else:
            if request.method == 'POST':
                #DATOS PARA GUARDAR GASTOS
                numorden = request.form['numord']
                zona = request.form['zona']
                mat = request.form['material']
                fecha = request.form['fecha']
                notcierre = request.form['notcierre']

                #DATOS PARA GUARDAR SCORE
                tipo = request.form['tiposervicio']
                
                if tipo == 'Instalacion':
                    puntaje = 10
                elif tipo == 'Mantenimiento':
                    puntaje = 5
                elif tipo == 'Corte':
                    puntaje = 2
                elif tipo == 'Reconexion':
                    puntaje = 2
                elif tipo == 'Traslado':
                    puntaje = 10
                elif tipo == 'Normalizacion':
                    puntaje = 5
                
                #####CONSULTAR NOMBRE TECNICO PARA GUARDAR CEDULA
                tec = full_name
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
                cur.execute(query,(tec,) )
                data = cur.fetchall()
                cur.close() 
                
                cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")

                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("INSERT INTO score (sc_idtec,sc_numorden,sc_tiposervicio,sc_puntaje,sc_fecha) VALUES (%s,%s,%s,%s,%s)", (cedula,numorden,tipo,puntaje,fecha))
                conn.commit()
                cur.close()

                if mat != "":
                    material = mat.split(',')
                    
                    ite = len(material)
                    y = 0
                    for x in range(0,int(ite/2)):
                        pass
                        ####INSERTAR GASTOS DE ZONA
                        '''cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute("INSERT INTO gastos_zona (gz_numorden,gz_zona,gz_descmaterial,gz_cantidad) VALUES (%s,%s,%s,%s)", (numorden,zona,material[y],material[y+1]))
                        conn.commit()
                        cur.close()
                        y+=2'''
                
                
                '''
                #ACTUALIZAR ESTADO DE ORDEN DE PENDIENTE A COMPLETADO
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""UPDATE asignacion_tarea SET at_estado = %s WHERE at_numsolicitud = %s """,('Completado', str(numord)))
                conn.commit()
                cur.close()'''

                #### INSERTAR NOTAS TECNICO
                '''cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("INSERT INTO notas (no_numord,no_idtecnico,no_notas,no_fecha,no_estado) VALUES (%s,%s,%s,%s,%s)", (numorden, cedula, notcierre, fecha, 'Completado'))
                conn.commit()
                cur.close()'''

                return redirect(url_for('ver_tareas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route("/time_chart")
def time_chart():
    
    legend = 'Temperatures'
    temperatures = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
                    61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
                    70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
    times = [time(hour=11, minute=14, second=15),
             time(hour=11, minute=14, second=30),
             time(hour=11, minute=14, second=45),
             time(hour=11, minute=15, second=00),
             time(hour=11, minute=15, second=15),
             time(hour=11, minute=15, second=30),
             time(hour=11, minute=15, second=45),
             time(hour=11, minute=16, second=00),
             time(hour=11, minute=16, second=15),
             time(hour=11, minute=16, second=30),
             time(hour=11, minute=16, second=45),
             time(hour=11, minute=17, second=00),
             time(hour=11, minute=17, second=15),
             time(hour=11, minute=17, second=30),
             time(hour=11, minute=17, second=45),
             time(hour=11, minute=18, second=00),
             time(hour=11, minute=18, second=15),
             time(hour=11, minute=18, second=30)]
        
    legend = 'Monthly performance at 50m Freestyle'
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dic"]

    values = [26.94, 26.70, 26.80, 25.1, 26.45, 26.43, 26.30, 26.25, 26.20, 26.35, 26.00, 25.00]
    return render_template('time_chart3.html', values=values, labels=labels, legend=legend)
    #return render_template('time_chart.html', values=temperatures, labels=times, legend=legend)


@app.route('/ver_notas')
def ver_notas():   
    if 'usuario' in session:
        
        tec = full_name
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
        cur.execute(query,(tec,) )
        data = cur.fetchall()
        cur.close() 
        cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT no_numord,no_notas,no_fecha,no_estado FROM notas WHERE no_idtecnico = %s"
        cur.execute(s,(cedula,)) # Execute the SQL
        notas = cur.fetchall()
        cur.close()    

        '''cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        m = "SELECT no_numord FROM notas WHERE no_idtecnico = %s"
        cur.execute(m,(cedula,)) # Execute the SQL
        o_s = cur.fetchall()
        cur.close()'''

        '''o_service = []
        for y in range(0,1):
            for t in o_s:
                o_service.append(str(t).replace("'","").replace(",","").replace("[","").replace("]",""))        
        
        cant_ordenes=len(o_s)  '''
        
        #### GASTOS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        f = "SELECT gz_numorden,gz_descmaterial, gz_cantidad FROM gastos_zona" #WHERE gz_numorden = %s"
        cur.execute(f)
        gastos = cur.fetchall()
        cur.close()
        #print(o_service[k])
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        f = "SELECT DISTINCT (gz_numorden) FROM gastos_zona "
        cur.execute(f)
        n_ord = cur.fetchall()
        cur.close()
        numorden = str(n_ord).replace("'","").replace("[","").replace("]","")

        if notas:
            return render_template('ver_notas.html', notas = notas, user = usu, gastos = gastos , numorden = numorden ,  fullname = full_name)#numorden2 = numorden2,)        
        else:
            return render_template('ver_notas.html', fullname = full_name)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/ver_indicadores')
def ver_indicadores():   
    if 'usuario' in session:
        return render_template('slider_tecnicos.html', user = usu)  

@app.route('/material')
def material():   
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT ma_codigo FROM material"
        cur.execute(s) # Execute the SQL
        mat = cur.fetchall()
        cur.close()
        
        mate = []
        for y in range(0,1):
            for f in mat:
               mate.append(str(f).replace("'","").replace("[","").replace("]",""))        

        materiales = str(mate).replace("'","")

        return render_template('material.html', materiales = materiales,  user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_material')
def listado_material():   
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM material"
        cur.execute(s) # Execute the SQL
        list_material = cur.fetchall()
        cur.close()
        return render_template('listado_material.html' , list_material = list_material, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'


@app.route('/add_material',  methods=['GET','POST'])
def add_material():  
    if 'usuario' in session and session['usuario'] == "admin":
        codigo = request.form['codigo']
        descripcion = request.form['descripcion']
        
        if codigo == "" or descripcion == "":
            return redirect(url_for('material'))
        else:
            if request.method == 'POST':    
                codigo = request.form['codigo']
                seccion = request.form['seccion']
                descripcion = request.form['descripcion']
                unimedida = request.form['unimedida']

                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("INSERT INTO material (ma_codigo,ma_seccion,ma_descripcion,ma_unidad) VALUES (%s,%s,%s,%s)", (codigo,seccion,descripcion,unimedida))
                conn.commit()
                cur.close()
                
                return redirect(url_for('material'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/asignar_material')
def asignar_material():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT zo_nombre FROM zonas"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        zonas = []
        for y in range(0,1):
            for t in tec:
                zonas.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c = "SELECT ma_descripcion FROM material"
        cur.execute(c) # Execute the SQL
        desc = cur.fetchall()
        cur.close()
        material = []
        for y in range(0,1):
            for t in desc:
                material.append(str(t).replace("'","").replace(",","").replace("[","").replace("]",""))

        return render_template('asignar_material.html', user = usu, zonas = zonas, material = material)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_am')
def listado_am():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        d = "SELECT am_zona,ma_descripcion,SUM(cantidad) As cant FROM (SELECT am_codmaterial,am_zona,SUM(CAST(am_cantidad AS INTEGER)) As cantidad FROM asignacion_material GROUP BY am_codmaterial,am_zona,am_cantidad) As tabla_1 LEFT JOIN (SELECT ma_codigo,ma_descripcion FROM material GROUP BY ma_descripcion,ma_codigo) As tabla_2 ON tabla_2.ma_codigo = tabla_1.am_codmaterial GROUP BY am_zona,ma_descripcion"
        #d = "SELECT am_zona,ma_descripcion,am_cantidad FROM asignacion_material INNER JOIN material ON asignacion_material.am_codmaterial = material.ma_codigo GROUP BY am_zona,ma_descripcion,am_cantidad"
        cur.execute(d)
        list_material = cur.fetchall()
        cur.close() 
        return render_template('listado_am.html', user = usu, list_material = list_material)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/traslado')
def traslado():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT zo_nombre FROM zonas"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        zonas = []
        for y in range(0,1):
            for t in tec:
                zonas.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c = "SELECT ma_descripcion FROM material"
        cur.execute(c) # Execute the SQL
        desc = cur.fetchall()
        cur.close()
        material = []
        for y in range(0,1):
            for t in desc:
                material.append(str(t).replace("'","").replace(",","").replace("[","").replace("]",""))
    
        return render_template('traslado.html', user = usu, zonas = zonas, material = material)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_traslado', methods=['POST'])
def add_traslado():
    if 'usuario' in session and session['usuario'] == "admin":
        
        if request.method == 'POST':
            zona1 = request.form['zona1']
            zona2 = request.form['zona2']
            material = request.form['mat']
            cantidad = request.form['cantidad']
            
            #CODIGO DE MATERIAL
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            query = '''SELECT ma_codigo FROM material WHERE ma_descripcion = %s''' 
            cur.execute(query,(material,))
            cm = cur.fetchall()
            cur.close() 
            codmaterial = str(cm).replace("[","").replace("]","").replace(",","").replace("'","")

            #SI EXISTE MATERIAL EN LA ZONA A TRASLADAR
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            query = '''SELECT am_codmaterial FROM asignacion_material WHERE am_zona = %s AND am_codmaterial = %s''' 
            cur.execute(query,(zona2,material,))
            existe_material = cur.fetchall()
            cur.close() 

            if existe_material:
                #CONSULTA CANTIDAD DE MATERIAL ZONA QUE TRASLADA
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT am_cantidad FROM asignacion_material WHERE am_zona = %s AND am_codmaterial = %s''' 
                cur.execute(query,(zona1,codmaterial,))
                cm1 = cur.fetchall()
                cur.close() 
                cant1 = str(cm1).replace("[","").replace("]","").replace(",","").replace("'","")

                cantidad1 = int(cant1) - int(cantidad)

                #CONSULTA CANTIDAD DE MATERIAL ZONA A TRASLADAR
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT SUM(CAST(am_cantidad AS INTEGER)) FROM asignacion_material WHERE am_zona = %s AND am_codmaterial = %s''' 
                cur.execute(query,(zona2,codmaterial,))
                cm2 = cur.fetchall()
                cur.close() 
                cant2 = str(cm2).replace("[","").replace("]","").replace(",","").replace("'","")

                cantidad2 = int(cant2) + int(cantidad)

                #UPDATE ZONA QUE TRASLADA
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""
                    UPDATE asignacion_material
                    SET am_cantidad = %s
                    WHERE am_zona = %s AND am_codmaterial = %s
                """,(cantidad1, zona1, codmaterial))
                conn.commit()
                cur.close()

                #UPDATE ZONA QUE TRASLADA
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""
                    UPDATE asignacion_material
                    SET am_cantidad = %s
                    WHERE am_zona = %s AND am_codmaterial = %s
                """,(cantidad2, zona2, codmaterial))
                conn.commit()
                cur.close()
            else:
                #CONSULTA CANTIDAD DE MATERIAL ZONA QUE TRASLADA
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT am_cantidad FROM asignacion_material WHERE am_zona = %s AND am_codmaterial = %s''' 
                cur.execute(query,(zona1,codmaterial,))
                cm1 = cur.fetchall()
                cur.close() 
                cant1 = str(cm1).replace("[","").replace("]","").replace(",","").replace("'","")

                if cm1:
                    cantidad1 = int(cant1) - int(cantidad)

                    #UPDATE ZONA QUE TRASLADA
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute("""
                        UPDATE asignacion_material
                        SET am_cantidad = %s
                        WHERE am_zona = %s AND am_codmaterial = %s
                    """,(cantidad1, zona1, codmaterial))
                    conn.commit()
                    cur.close()
                    
                    #INSERTAR MATERIAL QUE TRASLADA Y NO EXISTE
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute("INSERT INTO asignacion_material (am_zona,am_codmaterial,am_cantidad) VALUES (%s,%s,%s)", (zona2,codmaterial,cantidad))
                    conn.commit()
                    cur.close()
                else:
                    print("La zona que traslkada no tiene este material disponible")

            return redirect(url_for('traslado'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_asignacion_material', methods=['POST'])
def add_asignacion_material():
    if 'usuario' in session and session['usuario'] == "admin":
        cantidad = request.form['cantidad']
        
        if cantidad == "":
            return redirect(url_for('asignar_material'))
        else:
            if request.method == 'POST':
                zona = request.form['zona']
                material = request.form['mat']
                cantidad = request.form['cantidad']
                
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT ma_codigo FROM material WHERE ma_descripcion = %s''' 
                cur.execute(query,(material,))
                cm = cur.fetchall()
                cur.close()
                codmaterial = str(cm).replace("[","").replace("]","").replace(",","").replace("'","")
                
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT am_cantidad FROM asignacion_material WHERE am_zona = %s AND am_codmaterial = %s''' 
                cur.execute(query,(zona,codmaterial,))
                cm2 = cur.fetchall()
                cur.close() 
                cant2 = str(cm2).replace("[","").replace("]","").replace(",","").replace("'","")
            
                if cm:
                    cantidad2 = int(cant2) + int(cantidad)

                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute("""
                        UPDATE asignacion_material
                        SET am_cantidad = %s
                        WHERE am_zona = %s AND am_codmaterial = %s
                    """,(cantidad2, zona, codmaterial))
                    conn.commit()
                    cur.close()
                else:
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cur.execute("INSERT INTO asignacion_material (am_zona,am_codmaterial,am_cantidad) VALUES (%s,%s,%s)", (zona,codmaterial,cantidad))
                    conn.commit()
                    cur.close()
                
                return redirect(url_for('asignar_material'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/stock')
def stock():
    
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT zo_nombre FROM zonas"
        cur.execute(s) 
        z = cur.fetchall()
        cur.close()
        zonas = []
        for y in range(0,1):
            for t in z:
                zonas.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        if request.args.get('zona') == None:
            zone = 'Bosa'
        else:
            ### ID PARA CONSULTAR STOCK
            zone = request.args.get('zona')
    
        ### LLENAR STOCK
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        d = "SELECT gz_zona,ma_descripcion,ma_unidad,am_cantidad,SUM(CAST(gz_cantidad AS INTEGER)),(CAST(am_cantidad AS INTEGER)- SUM(CAST(gz_cantidad AS INTEGER))) As Disponible FROM asignacion_material INNER JOIN material ON asignacion_material.am_codmaterial = material.ma_codigo INNER JOIN gastos_zona ON gastos_zona.gz_descmaterial = material.ma_descripcion AND gastos_zona.gz_zona = asignacion_material.am_zona WHERE gz_zona = %s GROUP BY am_zona,ma_descripcion,am_cantidad,ma_unidad,gz_cantidad,gz_zona"
        cur.execute(d,(zone,))
        list_mat = cur.fetchall()
        cur.close() 
        
        return render_template('stock.html', zonas = zonas, user = usu, list_mat = list_mat, zone = zone)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/ubicacion/<id>')
def ubicacion(id):
    
    if 'usuario' in session and session['usuario'] == "admin": 
        
        ####TECNICOS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos WHERE te_identificacion = %s"
        cur.execute(s,(id,)) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        tecnicos = []
        for y in range(0,1):
            for t in tec:
                tecnicos.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        tec = str(tecnicos).replace("'","").replace("[","").replace("]","")
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        p = "SELECT ge_latitud FROM geolocalizacion WHERE ge_tecnico = %s"
        cur.execute(p,(tec,)) 
        l = cur.fetchall()
        cur.close()
        latitud = []
        for y in range(0,1):
            for q in l:
                latitud.append(str(q).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        lati = str(latitud).replace("'","").replace("[","").replace("]","")

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        j = "SELECT ge_longitud FROM geolocalizacion WHERE ge_tecnico = %s"
        cur.execute(j,(tec,)) 
        k = cur.fetchall()
        cur.close()
        longitud = []
        for y in range(0,1):
            for t in k:
                longitud.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))
        
        longi = str(longitud).replace("'","").replace("[","").replace("]","")
        
        return render_template('ubicacion.html', user = usu, tecnico = tec, latitud = lati, longitud = longi)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        #AL QUE ACTUALIZO
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (id,) )
        data = cur.fetchall()
        cur.close()
        
        #CONSULTAR ENTRE TODOS
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT te_identificacion FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        
        tecn = []
        for y in range(0,1):
            for f in tec:
               tecn.append(str(f).replace("'","").replace("[","").replace("]",""))        

        tecnicos = str(tecn).replace("'","")

        return render_template('edit2.html', tecnico = data[0], tecnicos = tecnicos, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_he/<cod>', methods = ['POST', 'GET'])
def get_tool(cod):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM herramientas WHERE he_codigo = %s', (cod,) )
        data = cur.fetchall()
        cur.close()
        
        #Traer todos los codigos
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT he_codigo FROM herramientas")
        herramienta = cur.fetchall()
        cur.close()

        return render_template('edit_herramienta.html', herramientas = data[0], herramienta = herramienta, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_ma/<cod>', methods = ['POST', 'GET'])
def get_material(cod):
    if 'usuario' in session and session['usuario'] == "admin": 

        #Material a editar si es el mismo
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM material WHERE ma_codigo = %s', (cod,) )
        data = cur.fetchall()
        cur.close()
        
        #Traer todos los codigos
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT ma_codigo FROM material")
        materiales = cur.fetchall()
        cur.close()
        
        return render_template('edit_material.html', material = data[0], materiales = materiales, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_am', methods = ['POST', 'GET'])
def get_asig_material():
    if 'usuario' in session and session['usuario'] == "admin": 

        parametros = request.args.get('parametros')
        lista = parametros.split(',')

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = 'SELECT am_zona,ma_descripcion,am_cantidad,am_codmaterial FROM asignacion_material INNER JOIN material ON material.ma_codigo = asignacion_material.am_codmaterial  WHERE am_zona = ' + "'"  + (lista[0]) + "' AND ma_descripcion = '"  + (lista[1]) + "'  GROUP BY am_zona,ma_descripcion,am_cantidad,am_codmaterial"
        cur.execute(query)
        data = cur.fetchall()
        cur.close() 

        return render_template('edit_am.html', asignacion_material = data[0], user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_ah', methods = ['POST', 'GET'])
def get_asig_herramienta():
    if 'usuario' in session and session['usuario'] == "admin": 

        parametros = request.args.get('parametros')
        lista = parametros.split(',')
        
        ##### CODIGO HERRAMIENTA
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT he_codigo FROM herramientas WHERE he_descripcion = %s''' 
        cur.execute(query,(lista[1],))
        cm = cur.fetchall()
        cur.close() 
        codherr = str(cm).replace("[","").replace("]","").replace(",","").replace("'","")

        #CEDULA TECNICO
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ',te_apellidos) = %s''' 
        cur.execute(query,(lista[0],))
        tecnico = cur.fetchall()
        cur.close() 
        idtec = str(tecnico).replace("[","").replace("]","").replace(",","").replace("'","")

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT CONCAT(te_nombres,' ',te_apellidos) As tecnico, he_descripcion, ah_cantidad, ah_codherr FROM asignacion_herramienta INNER JOIN herramientas ON asignacion_herramienta.ah_codherr = herramientas.he_codigo INNER JOIN tecnicos ON tecnicos.te_identificacion = asignacion_herramienta.ah_idtec WHERE ah_idtec = " + "'" + idtec + "'" + " AND ah_codherr = " + "'" + codherr + "'" + " GROUP BY te_nombres,te_apellidos,he_descripcion,ah_cantidad,ah_codherr"
        cur.execute(query)
        data = cur.fetchall()
        cur.close() 
        
        return render_template('edit_ah.html', asignacion_herramienta = data[0], user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_os/<os>', methods = ['POST', 'GET'])
def get_os(os):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT at_numsolicitud,at_idtecnico,at_zona,at_tipo,at_usuario,at_direccion,at_detalle,at_horario,at_observ_orden FROM asignacion_tarea WHERE at_numsolicitud = %s', (os,) )
        data = cur.fetchall()
        cur.close()
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        tecnicos = []
        for p in range(0,1):
            for r in tec:
                tecnicos.append(str(r).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT zo_nombre FROM zonas"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        zonas = []
        for y in range(0,1):
            for t in tec:
                zonas.append(str(t).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        return render_template('edit_os2.html', os = data[0], tecnicos = tecnicos, zonas = zonas, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update_os/<os>', methods=['POST'])
def update_orden(os):
    if 'usuario' in session and session['usuario'] == "admin": 
        tec = request.form['idtec']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
        cur.execute(query,(tec,) )
        data = cur.fetchall()
        cur.close() 
        cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")

        if request.method == 'POST':
            zona = request.form['zona']
            tipo = request.form['tipo']
            red = request.form['red']
            usuario = request.form['usuario']
            direccion = request.form['direccion']
            detalle = request.form['detalle']
            de = request.form['de']
            a = request.form['a']
            observacion = request.form['observacion']
            horario = de + " - " + a

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                UPDATE asignacion_tarea 
                SET at_idtecnico = %s,
                    at_zona = %s,
                    at_tipo = %s,
                    at_usuario = %s,
                    at_red = %s,
                    at_direccion = %s,
                    at_detalle = %s,
                    at_horario = %s,
                    at_observ_orden = %s
                WHERE at_numsolicitud = %s
            """,(cedula, zona, tipo, red, usuario, direccion, detalle, horario, observacion, os))
            conn.commit()
            cur.close()
        
            return redirect(url_for('listado_tareas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update_he/<cod>', methods=['POST'])
def update_herramienta(cod):
    if 'usuario' in session and session['usuario'] == "admin": 
        if request.method == 'POST':
            descripcion = request.form['desc']
            cantidad = request.form['cant']
            estado = request.form['estado']
                        
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                UPDATE herramientas
                SET he_descripcion = %s,
                    he_cantidad = %s,
                    he_estado = %s
                WHERE he_codigo = %s
            """,(descripcion, cantidad, estado, cod))
            conn.commit()
            cur.close()
            
            return redirect(url_for('listado_herramientas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update_am/<cod>', methods=['POST'])
def update_asignacion_material(cod):
    if 'usuario' in session and session['usuario'] == "admin": 
        if request.method == 'POST':
            cantidad = request.form['cant']
            zona = request.form['zone']
                  
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                UPDATE asignacion_material
                SET am_cantidad = %s
                WHERE am_codmaterial = %s AND am_zona = %s 
            """,(cantidad, cod, zona))
            conn.commit()
            cur.close()            
            return redirect(url_for('listado_am'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update_ah/<cod>', methods=['POST'])
def update_asignacion_herramienta(cod):
    if 'usuario' in session and session['usuario'] == "admin": 
        if request.method == 'POST':
            cantidad = request.form['cant']
            tecnico = request.form['idtec']

            #CEDULA TECNICO
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ',te_apellidos) = %s''' 
            cur.execute(query,(tecnico,))
            tecnico = cur.fetchall()
            cur.close() 
            idtec = str(tecnico).replace("[","").replace("]","").replace(",","").replace("'","")

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                UPDATE asignacion_herramienta
                SET ah_cantidad = %s
                WHERE ah_idtec = %s AND ah_codherr = %s 
            """,(cantidad, idtec, cod))
            conn.commit()
            cur.close()            

            return redirect(url_for('listado_ah'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update/<id>', methods=['POST'])
def update_tecnico(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        if request.method == 'POST':
            ident = request.form['id']
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            telefono = request.form['telefono']
            direccion = request.form['direccion']
            email = request.form['email']
            tipo = request.form['tipo']
            nivel = request.form['nivel']
            
            #GUARDAR FOTO
            foto = request.files['foto']
            #name = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], id +".jpg"))

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                UPDATE tecnicos 
                SET te_identificacion = %s,
                    te_nombres = %s,
                    te_apellidos = %s,
                    te_telefono = %s,
                    te_direccion = %s,
                    te_email = %s,
                    te_tipo = %s,
                    te_nivel = %s
                WHERE te_identificacion = %s
            """,(ident, nombres, apellidos, telefono, direccion, email, tipo, nivel, id))
            conn.commit()
            cur.close()
            return redirect(url_for('listado_tecnicos_activos'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update_ma/<cod>', methods=['POST'])
def update_material(cod):
    if 'usuario' in session and session['usuario'] == "admin": 
        if request.method == 'POST':
            codigo = request.form['codigo']
            seccion = request.form['seccion']
            descripcion = request.form['desc']
            unidad = request.form['unidad']
            
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                UPDATE material
                SET ma_codigo = %s,
                    ma_seccion = %s,
                    ma_descripcion = %s,
                    ma_unidad = %s
                WHERE ma_codigo = %s
            """,(codigo, seccion, descripcion, unidad, cod))
            conn.commit()
            cur.close()
            return redirect(url_for('listado_material'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/update_os_incompleta/<os>', methods = ['POST','GET'])
def update_orden_incompleta(os):
    if 'usuario' in session and session['usuario'] == "admin":    
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE asignacion_tarea 
            SET at_estado = %s
            WHERE at_numsolicitud = %s
        """,('Completado', os))
        conn.commit()
        cur.close()
        return redirect(url_for('tareas')) 
    else:
        return 'No tiene permiso de acceso a esa ruta.'    

@app.route('/reintegrar/<tec>', methods = ['POST','GET'])
def reintegro_tecnico(tec):
    print(tec)
    #CEDULA TECNICO
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ',te_apellidos) = %s''' 
    cur.execute(query,(tec,))
    tecnico = cur.fetchall()
    cur.close() 
    idtec = str(tecnico).replace("[","").replace("]","").replace(",","").replace("'","")

    if 'usuario' in session and session['usuario'] == "admin":    
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE tecnicos 
            SET te_estado = %s
            WHERE te_identificacion = %s
        """,(True, idtec))
        conn.commit()
        cur.close()
        return redirect(url_for('listado_tecnicos_inactivos')) 
    else:
        return 'No tiene permiso de acceso a esa ruta.'    

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_tecnico(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        fech = str(datetime.today().strftime('%d-%m-%Y'))
        fecha = fech[:10] 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE tecnicos
            SET te_fechasalida = %s,
                te_estado = %s
            WHERE te_identificacion = %s
        """,(fecha,False, id))
        conn.commit()
        cur.close()
            
        return redirect(url_for('listado_tecnicos_inactivos'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'     

@app.route('/delete_am', methods = ['POST','GET'])
def delete_asignacion_material():
    if 'usuario' in session and session['usuario'] == "admin": 

        parametros = request.args.get('parametros')
        lista = parametros.split(',')

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT ma_codigo FROM material WHERE ma_descripcion = %s''' 
        cur.execute(query,(lista[1],))
        cm = cur.fetchall()
        cur.close() 

        codmaterial = str(cm).replace("[","").replace("]","").replace(",","").replace("'","")
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('DELETE FROM asignacion_material WHERE am_zona = ' + "'"  + (lista[0]) + "' AND am_codmaterial = " + "'"  + (codmaterial) + "'") 
        conn.commit() 
        cur.close()
        
        return redirect(url_for('listado_am'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'    

@app.route('/delete_ah', methods = ['POST','GET'])
def delete_asignacion_herramienta():
    if 'usuario' in session and session['usuario'] == "admin": 

        parametros = request.args.get('parametros')
        lista = parametros.split(',')

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ',te_apellidos) = %s''' 
        cur.execute(query,(lista[0],))
        cm = cur.fetchall()
        cur.close() 
        idtec = str(cm).replace("[","").replace("]","").replace(",","").replace("'","")
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = '''SELECT he_codigo FROM herramientas WHERE he_descripcion = %s''' 
        cur.execute(query,(lista[1],))
        cm1 = cur.fetchall()
        cur.close() 
        codherr = str(cm1).replace("[","").replace("]","").replace(",","").replace("'","")
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('DELETE FROM asignacion_herramienta WHERE ah_idtec = ' + "'"  + (idtec) + "' AND ah_codherr = " + "'"  + (codherr) + "'") 
        conn.commit() 
        cur.close()
        
        return redirect(url_for('listado_ah'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'    

@app.route('/delete_ma/<string:codigo>', methods = ['POST','GET'])
def delete_material(codigo):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('DELETE FROM material WHERE ma_codigo = ' + "'" + (codigo)+ "'")
        conn.commit() 
        cur.close()
        return redirect(url_for('listado_material'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'    

########################## INICIO DE SESION ####################
@login_manager_app.user_loader
def load_user(id):
    pass
    return ModelUser.get_by_id(conn, id)

@app.route('/login', methods=['GET', 'POST'])
def login():

    global full_name, usu
    if request.method == 'POST':
        us = request.form['username']
        session['usuario'] = us
        user = User(0, request.form['username'], request.form['password'])        
        logged_user = ModelUser.login(user)
        
        if logged_user != None:
            usu = logged_user.username
            full_name = logged_user.fullname
            if logged_user.password:
                login_user(logged_user)
                
                session['usuario'] = logged_user.username
                return redirect(url_for('home'))
            else:
                flash("Invalid password...")
                return render_template('login.html')
        else:
            flash("User not found...")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/usuario')
def usuario():
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tec = cur.fetchall()
        cur.close()
        tecnicos = []
        for p in range(0,1):
            for r in tec:
                tecnicos.append(str(r).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

        return render_template('usuario.html', tecnicos = tecnicos, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'  

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        username = request.form['username']
        password = request.form['password']
        
        if username == "" or password == "":
            return redirect(url_for('usuario'))
        else:            
            if request.method == 'POST':
                username = request.form['username']
                passw = request.form['password']
                fullname = request.form['fullname']
                
                password = User.create_password(passw)

                cur.execute("INSERT INTO log_in (lo_username, lo_password, lo_fullname) VALUES (%s,%s,%s)", (username, password, fullname))
                conn.commit()
                cur.close()
            
                return redirect(url_for('usuario'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'  

@app.route('/add_localizacion', methods = ['GET'])
def add_localizacion():
    
    parametros = request.args.get('parametros')
    print(parametros)
    lista = parametros.split(',')

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT ge_tecnico FROM geolocalizacion WHERE ge_tecnico = %s"
    cur.execute(s,(lista[0],)) # Execute the SQL
    tec = cur.fetchall()
    cur.close()

    if tec:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE geolocalizacion 
            SET ge_latitud = %s,
                ge_longitud = %s
            WHERE ge_tecnico = %s
        """,(lista[1],lista[2], lista[0]))
        conn.commit()
        cur.close()
    else:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("INSERT INTO geolocalizacion (ge_tecnico, ge_latitud, ge_longitud) VALUES (%s,%s,%s)", (lista[0], lista[1], lista[2]))
        conn.commit()
        cur.close()

    return redirect(url_for('ver_tareas'))   
    #return render_template('index.html', user = usu, fullname = full_name)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    legend = 'Historial Trimestre'
    labels = ["Jan", "Feb", "Mar", "Apr", "May"]#, "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dic"]

    values = [26.94, 26.70, 30.80, 25.1, 26.45]#, 26.43, 26.30, 26.25, 26.20, 26.35, 26.00, 25.00]
    return render_template('index.html', legend = legend, labels = labels, values = values, user = usu, fullname = full_name)

@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == "__main__":
    #app.run(debug=True)
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()