from genericpath import exists
from xml.dom.minidom import Element
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2 
import psycopg2.extras
from datetime import datetime
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
        s = "SELECT * FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tecnicos = cur.fetchall()
        cur.close()
        return render_template('tecnicos2.html',tecnicos = tecnicos, user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_tecnico', methods=['POST'])
def add_tecnico():
    if 'usuario' in session and session['usuario'] == "admin":
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        id = request.form['id']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        nivel = request.form['nivel']

        if id == "" or nombres == "" or apellidos == "" or telefono == "" or direccion == "":
            
            return redirect(url_for('tecnicos'))
        else:    
            id = request.form['id']
            ident = int(id)
            cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (str(ident),) )
            data = cur.fetchall()
            
            if data:
                cur.close()
                return redirect(url_for('tecnicos'))
            else:
                if request.method == 'POST':
                    id = request.form['id']
                    nombres = request.form['nombres']
                    apellidos = request.form['apellidos']
                    telefono = request.form['telefono']
                    direccion = request.form['direccion']
                    nivel = request.form['nivel']
                    
                    #GUARDAR FOTO
                    foto = request.files['foto']
                    #name = secure_filename(foto.filename)
                    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], id+".jpg"))

                    cur.execute("INSERT INTO tecnicos (te_identificacion, te_nombres, te_apellidos, te_telefono, te_direccion, te_nivel) VALUES (%s,%s,%s,%s,%s,%s)", (str(id), nombres, apellidos, telefono, direccion, nivel))
                    conn.commit()
                    cur.close()
                    
                    return redirect(url_for('tecnicos'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_tecnicos')
def listado_tecnicos():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM tecnicos"
        cur.execute(s) # Execute the SQL
        tecnicos = cur.fetchall()
        cur.close()
        return render_template('listado_tecnicos.html',tecnicos = tecnicos, user = usu)
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
        return render_template('herramientas.html', user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/listado_herramientas')
def listado_herramientas():
    if 'usuario' in session and session['usuario'] == "admin":
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM herramientas"
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
                    flash('Ingrese valores correctos')
                    return redirect(url_for('asignar_herramienta'))    
                else: 
                    if int(cantidad) > int(c_herr):
                        flash('No hay suficiente '+ codher +' en stock')
                        return redirect(url_for('asignar_herramienta'))    
                    else:
                        cant_nueva = int(c_herr) - int(cantidad)
    
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute("INSERT INTO asignacion_herramienta (ah_idtec,ah_codherr,ah_cantidad,ah_fecha) VALUES (%s,%s,%s,%s)", (idtec,codherr,cantidad,fecha))
                        conn.commit()
                        cur.close()
        
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute("""
                            UPDATE herramientas
                            SET he_cantidad = %s
                            WHERE he_codigo = %s
                        """,(cant_nueva, codherr))
                        conn.commit()
                        cur.close()

                        flash('Added Tool Assignment')
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
            flash('Agregue todos los datos')
            return redirect(url_for('zonas'))
        else:    
            if request.method == 'POST':
                zona = request.form['zona']
                cur.execute("INSERT INTO zonas (zo_nombre, zo_estado) VALUES (%s,%s)", (zona,True))
                conn.commit()
                cur.close()
                flash('Zone Added Successfully')
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

@app.route('/ver_tareas')
def ver_tareas():
    if 'usuario' in session:
        global idtec,asignaciones,horarios
        hora1 = ""
        hora11 = ""
        hora2 = ""
        hora3 = ""
        hora4 = ""
        hora5 = ""
        expirado1 = ""
        expirado11 = ""
        expirado2 = ""
        expirado3 = ""
        expirado4 = ""
        expirado5 = ""

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
        s = "SELECT at_numsolicitud,CONCAT(te_nombres,' ',te_apellidos),at_zona,at_tipo,UPPER(at_red),at_usuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha FROM asignacion_tarea INNER JOIN tecnicos ON asignacion_tarea.at_idtecnico = tecnicos.te_identificacion WHERE at_idtecnico = %s GROUP BY at_idtecnico,at_numsolicitud,te_nombres,te_apellidos,at_zona,at_tipo,at_red,at_usuario,at_direccion,at_detalle,at_horario,at_observ_orden,at_estado,at_fecha"
        cur.execute(s,(idtec,))
        asignaciones = cur.fetchall()
        cur.close() 
        
        formato = "%H:%M:%S"        
        h_actual = datetime.strptime(str(datetime.today().strftime('%H:%M:%S')), formato)
        
        for item in horarios:

            if item == '8 - 10':
                h_ini1 = datetime.strptime('10:00:00', formato)
                if h_actual > h_ini1 :
                    expirado1 = 1
                    hora1 = h_actual - h_ini1
                else:
                    expirado1 = 0
                    hora1 = h_ini1 - h_actual    
            
            if item == '8 - 9':
                h_ini11 = datetime.strptime('09:00:00', formato)
                if h_actual > h_ini11 :
                    expirado11 = 1
                    hora11 = h_actual - h_ini11
                else:
                    expirado11 = 0
                    hora11 = h_ini11 - h_actual    

            if item == '10 - 12':
                h_ini2 = datetime.strptime('12:00:00', formato)
                if h_actual > h_ini2 :
                    expirado2 = 1
                    hora2 = h_actual - h_ini2
                else:
                    expirado2 = 0
                    hora2 = h_ini2 - h_actual
            '''else:
                expirado2 = 0
                hora2 = h_actual'''
                #return render_template('ver_tareas.html', asignaciones = asignaciones, fullname = full_name, user = usu, hora2 = hora2, expirado2 = expirado2)
            
            if item == '12 - 14':
                h_ini3 = datetime.strptime('14:00:00', formato)
                if h_actual > h_ini3 :
                    expirado3 = 1
                    hora3 = h_actual - h_ini3
                else:
                    expirado3 = 0
                    hora3 = h_ini3 - h_actual
            '''else:
                expirado3 = 0
                hora3 = h_actual'''
                #return render_template('ver_tareas.html', asignaciones = asignaciones, fullname = full_name, user = usu, hora3 = hora3, expirado3 = expirado3)
                
            if item == '14 - 16':
                h_ini4 = datetime.strptime('16:00:00', formato)
                if h_actual > h_ini4 :
                    expirado4 = 1
                    hora4 = h_actual - h_ini4
                else:
                    expirado4 = 0
                    hora4 = h_ini4 - h_actual
                #return render_template('ver_tareas.html', asignaciones = asignaciones, fullname = full_name, user = usu, hora4 = hora4, expirado4 = expirado4)
            '''else:
                expirado4 = 0
                hora4 = h_actual'''

            if item == '16 - 18':
                h_ini5 = datetime.strptime('18:00:00', formato)
                if h_actual > h_ini5 :
                    expirado5 = 1
                    hora5 = h_actual - h_ini5
                else:
                    expirado5 = 0
                    hora5 = h_ini5 - h_actual                    
                #return render_template('ver_tareas.html', asignaciones = asignaciones, fullname = full_name, user = usu, hora5 = hora5, expirado5 = expirado5)
            '''else:
                expirado5 = 0
                hora5 = h_actual'''

        return render_template('ver_tareas.html', asignaciones = asignaciones, fullname = full_name, user = usu, hora1 = hora1, expirado1 = expirado1, hora2 = hora2, expirado2 = expirado2, hora3 = hora3, expirado3 = expirado3, hora4 = hora4, expirado4 = expirado4, hora5 = hora5, expirado5 = expirado5, hora11 = hora11, expirado11 = expirado11)
    else:
        return 'No tiene permiso de acceso a esa ruta.'    
       
@app.route('/add_tareas', methods=['POST'])
def add_tareas():
    if 'usuario' in session and session['usuario'] == "admin":
        usuario = request.form['usuario']
        direccion = request.form['direccion']
        detalle = request.form['detalles']
        observ = request.form['observaciones']

        fech = str(datetime.today().strftime('%d-%m-%Y %H:%M'))
        fecha = fech[:10]

        if usuario == "" or direccion == "" or detalle == "" or observ == "":
            flash('Agregue todos los datos')
            return redirect(url_for('tareas'))
        else:   
            tec = request.form['idtec']
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
            cur.execute(query,(tec,) )
            data = cur.fetchall()
            cur.close() 
            cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")
            
            #if data:
            #    cur.close()
            #    flash('Ya existe el número de identificación')
            #    return redirect(url_for('tecnicos'))
            #else:
            if request.method == 'POST':
                numsol = request.form['numsol']
                zona = request.form['zona']
                tipo = request.form['tipo']
                red = request.form['red']
                usuario = request.form['usuario']
                direccion = request.form['direccion']
                detalle = request.form['detalles']
                de = request.form['de']
                a = request.form['a']
                observ = request.form['observaciones']
                fecha = datetime.today()
                horario = de + " - " + a

                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("INSERT INTO asignacion_tarea (at_numsolicitud, at_idtecnico, at_zona, at_tipo, at_red, at_usuario, at_direccion, at_detalle, at_horario, at_observ_orden, at_estado, at_fecha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (numsol,cedula,zona,tipo,red,usuario,direccion,detalle,horario,observ,'Pendiente',fecha))
                conn.commit()
                cur.close()
                flash('Task Added Successfully')
                return redirect(url_for('tareas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/notas')
def notas():   
    if 'usuario' in session :
        orden = request.args.get('orden')
        zona = request.args.get('zona')
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

        return render_template('notas.html', fecha = fecha, orden = orden, zona = zona ,material = material ,user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_notas',  methods=['POST'])
def add_notas():  
    if 'usuario' in session: 
        notcierre = request.form['notcierre']
        cantidad = request.form['dat[]']
        if notcierre == "" or cantidad =="":
            flash("Agregue todos los datos")
            return redirect(url_for('notas'))
        else:
            if request.method == 'POST':
                numorden = request.form['numord']
                zona = request.form['zona']
                mat = request.form['material']
                fecha = request.form['fecha']
                notcierre = request.form['notcierre']

                #####CONSULTAR NOMBRE TECNICO PARA GUARDAR CEDULA
                tec = full_name
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = '''SELECT te_identificacion FROM tecnicos WHERE CONCAT(te_nombres,' ', te_apellidos) = %s''' 
                cur.execute(query,(tec,) )
                data = cur.fetchall()
                cur.close() 
                
                cedula = str(data).replace("[","").replace("]","").replace("(","").replace(")","").replace(",","").replace("'","")

                if mat != "":
                    material = mat.split(',')
                    
                    ite = len(material)
                    y = 0
                    for x in range(0,int(ite/2)):
                        ####INSERTAR GASTOS DE ZONA
                        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                        cur.execute("INSERT INTO gastos_zona (gz_numorden,gz_zona,gz_descmaterial,gz_cantidad) VALUES (%s,%s,%s,%s)", (numorden,zona,material[y],material[y+1]))
                        conn.commit()
                        cur.close()
                        y+=2
                
                
                '''
                #ACTUALIZAR ESTADO DE ORDEN DE PENDIENTE A COMPLETADO
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("""UPDATE asignacion_tarea SET at_estado = %s WHERE at_numsolicitud = %s """,('Completado', str(numord)))
                conn.commit()
                cur.close()'''

                #### INSERTAR NOTAS TECNICO
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("INSERT INTO notas (no_numord,no_idtecnico,no_notas,no_fecha,no_estado) VALUES (%s,%s,%s,%s,%s)", (numorden, cedula, notcierre, fecha, 'Completado'))
                conn.commit()
                cur.close()

                return redirect(url_for('ver_tareas'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'

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
        return render_template('material.html' , user = usu)
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
            flash('Agregue todos los datos')
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
                flash('Add Material')
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
        d = "SELECT am_zona,ma_descripcion,am_cantidad FROM asignacion_material INNER JOIN material ON asignacion_material.am_codmaterial = material.ma_codigo GROUP BY am_zona,ma_descripcion,am_cantidad"
        cur.execute(d)
        list_material = cur.fetchall()
        cur.close() 
        return render_template('listado_am.html', user = usu, list_material = list_material)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/add_asignacion_material', methods=['POST'])
def add_asignacion_material():
    if 'usuario' in session and session['usuario'] == "admin":
        cantidad = request.form['cantidad']
        
        if cantidad == "":
            flash('Agregue todos los datos')
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
                cur.execute("INSERT INTO asignacion_material (am_zona,am_codmaterial,am_cantidad) VALUES (%s,%s,%s)", (zona,codmaterial,cantidad))
                conn.commit()
                cur.close()
                flash('Added Material Assignment')
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

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (id,) )
        data = cur.fetchall()
        cur.close()
        
        return render_template('edit2.html', tecnico = data[0], user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_he/<cod>', methods = ['POST', 'GET'])
def get_tool(cod):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM herramientas WHERE he_codigo = %s', (cod,) )
        data = cur.fetchall()
        cur.close()
        
        return render_template('edit_herramienta.html', herramientas = data[0], user = usu)
    else:
        return 'No tiene permiso de acceso a esa ruta.'

@app.route('/edit_ma/<cod>', methods = ['POST', 'GET'])
def get_material(cod):
    if 'usuario' in session and session['usuario'] == "admin": 

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM material WHERE ma_codigo = %s', (cod,) )
        data = cur.fetchall()
        cur.close()
        
        return render_template('edit_material.html', material = data[0], user = usu)
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
            a = request.form['a']
            de = request.form['de']
            observacion = request.form['observacion']
            horario = a + " - " + de

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
            flash('Service Order Updated Successfully')
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
            
            return redirect(url_for('herramientas'))
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

@app.route('/update/<id>', methods=['POST'])
def update_tecnico(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        if request.method == 'POST':
            ident = request.form['id']
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            telefono = request.form['telefono']
            direccion = request.form['direccion']
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
                    te_nivel = %s
                WHERE te_identificacion = %s
            """,(ident, nombres, apellidos, telefono, direccion, nivel, id))
            
            conn.commit()
            cur.close()
            return redirect(url_for('listado_tecnicos'))
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
            flash('Material Updated Successfully')
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
        flash('Technical Updated Successfully')
        conn.commit()
        cur.close()
        return redirect(url_for('tareas')) 
    else:
        return 'No tiene permiso de acceso a esa ruta.'    

@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_tecnico(id):
    if 'usuario' in session and session['usuario'] == "admin": 
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('DELETE FROM tecnicos WHERE te_identificacion = ' + "'" + (id)+ "'")
        conn.commit() 
        cur.close()
        
        return redirect(url_for('tecnicos'))
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
            flash('Agregue todos los datos')
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
                flash('User Added Successfully')
                return redirect(url_for('usuario'))
    else:
        return 'No tiene permiso de acceso a esa ruta.'  

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('index.html', user = usu, fullname = full_name)

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