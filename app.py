from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2 #pip install psycopg2 pip
import psycopg2.extras
 
app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"
 
DB_HOST = "127.0.0.1"
DB_NAME = "gestion_tecnica"
DB_USER = "postgres"
DB_PASS = "12345678"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tecnicos')
def tecnicos():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM tecnicos"
    cur.execute(s) # Execute the SQL
    list_users = cur.fetchall()
    cur.close()
    return render_template('tecnicos.html',list_users = list_users)

@app.route('/tareas')
def tareas():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT CONCAT(te_nombres,' ',te_apellidos) FROM tecnicos"
    cur.execute(s) # Execute the SQL
    tec = cur.fetchall()
    cur.close()
    l = []
    for p in range(0,1):
        for r in tec:
            l.append(str(r).replace("(","").replace(")","").replace("'","").replace(",","").replace("[","").replace("]",""))

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM asignacion_tarea"
    cur.execute(s) # Execute the SQL
    tareas = cur.fetchall()
    cur.close()


    return render_template('tareas.html', tecnicos = l, asignaciones = tareas)

@app.route('/ver_tareas')
def ver_tareas():
    idtec = '3'
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM asignacion_tarea WHERE at_idtecnico = %s"
    cur.execute(s,(idtec,)) # Execute the SQL
    asignaciones = cur.fetchall()
    cur.close()
    return render_template('ver_tareas.html', asignaciones = asignaciones)


@app.route('/add_tareas', methods=['POST'])
def add_tareas():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    numsol1 = '1001'#request.form['numsol']
    idtec = request.form['idtec']
    zona = request.form['zona']
    tipo = request.form['tipo']
    usuario = request.form['usuario']
    direccion = request.form['direccion']
    detalle = request.form['detalles']
    horario = request.form['horario']
    observ = request.form['observaciones']
    
    if numsol1 == "" or idtec == "" or usuario == "" or direccion == "" or detalle == "" or observ == "":
        flash('Agregue todos los datos')
        return redirect(url_for('add_tareas'))
    else:    
        #id = request.form['id']
        #ident = int(id)
        #cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (ident,) )
        #data = cur.fetchall()
        
        #if data:
        #    cur.close()
        #    flash('Ya existe el número de identificación')
        #    return redirect(url_for('tecnicos'))
        #else:
        if request.method == 'POST':
            numsol = 1001
            #request.form['numsol']
            idtec = request.form['idtec']
            zona = request.form['zona']
            tipo = request.form['tipo']
            usuario = request.form['usuario']
            direccion = request.form['direccion']
            detalle = request.form['detalles']
            horario = request.form['horario']
            observ = request.form['observaciones']
            #fecha = request.form['fecha']

            cur.execute("INSERT INTO asignacion_tarea (at_numsolicitud, at_idtecnico, at_zona, at_tipo, at_usuario, at_direccion, at_detalle, at_horario, at_observ_orden, at_estado, at_fecha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (numsol,str(idtec),zona,tipo,usuario,direccion,detalle,horario,observ,'Pendiente','27/02/2022'))
            conn.commit()
            cur.close()
            flash('Task Added Successfully')
            return redirect(url_for('tareas'))

@app.route('/add_tecnico', methods=['POST'])
def add_tecnico():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    id = request.form['id']
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']
    telefono = request.form['telefono']
    direccion = request.form['direccion']
    nivel = request.form['nivel']

    if id == "" or nombres == "" or apellidos == "" or telefono == "" or direccion == "":
        flash('Agregue todos los datos')
        return redirect(url_for('tecnicos'))
    else:    
        id = request.form['id']
        ident = int(id)
        cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (str(ident),) )
        data = cur.fetchall()
        
        if data:
            cur.close()
            flash('Ya existe el número de identificación')
            return redirect(url_for('tecnicos'))
        else:
            if request.method == 'POST':
                id = request.form['id']
                nombres = request.form['nombres']
                apellidos = request.form['apellidos']
                telefono = request.form['telefono']
                direccion = request.form['direccion']
                nivel = request.form['nivel']
    
                cur.execute("INSERT INTO tecnicos (te_identificacion, te_nombres, te_apellidos, te_telefono, te_direccion, te_nivel) VALUES (%s,%s,%s,%s,%s,%s)", (str(id), nombres, apellidos, telefono, direccion, nivel))
                conn.commit()
                cur.close()
                flash('Technical Added Successfully')
                return redirect(url_for('tecnicos'))

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM tecnicos WHERE te_identificacion = %s', (id,) )
    data = cur.fetchall()
    cur.close()
    
    return render_template('edit.html', tecnico = data[0])
 
@app.route('/update/<id>', methods=['POST'])
def update_tecnico(id):
    if request.method == 'POST':
        ident = request.form['id']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        nivel = request.form['nivel']
         
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
        flash('Technical Updated Successfully')
        conn.commit()
        cur.close()
        return redirect(url_for('tecnicos'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_tecnico(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM tecnicos WHERE te_identificacion = {0}'.format(id))
    conn.commit() 
    cur.close()
    flash('Technical Deleted Successfully')
    return redirect(url_for('tecnicos'))
 
if __name__ == "__main__":
    app.run(debug=True)
