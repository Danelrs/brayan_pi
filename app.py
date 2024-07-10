from flask import Flask, request, redirect, url_for, flash, render_template
import pyodbc
import re

app = Flask(__name__)
app.secret_key = 'mi_secreto'

# Configuración de la conexión a la base de datos
conn_str = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=ALFREDO-DANEL-R;DATABASE=PREGNANCY2;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def is_valid_email(email):
    # Expresión regular para validar correo electrónico
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/')
def LandingPage():
    return render_template('LandingPage.html')

@app.route('/people')
def index():
    cursor.execute("SELECT * FROM Personas")
    personas = cursor.fetchall()
    return render_template('index.html', personas=personas)

@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ap_paterno = request.form['ap_paterno']
        ap_materno = request.form['ap_materno']
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion_id = request.form.get('direccion_id')  # Asumimos que `direccion_id` es opcional

        # Verificar que todos los campos requeridos estén presentes
        if not all([nombre, ap_paterno, ap_materno, telefono, correo]):
            flash("Todos los campos son requeridos.")
            return redirect(url_for('crear'))

        # Validar que el `telefono` contenga solo números y no tenga más de 10 dígitos
        if not telefono.isdigit() or len(telefono) > 10:
            flash("El teléfono debe contener solo números y no puede tener más de 10 dígitos.")
            return redirect(url_for('crear'))

        # Validar que el `correo` tenga un formato válido
        if not is_valid_email(correo):
            flash("El correo electrónico no es válido.")
            return redirect(url_for('crear'))

        # Verificar que el `direccion_id` sea opcional
        if direccion_id:
            cursor.execute("SELECT COUNT(*) FROM Direcciones WHERE id = ?", (direccion_id,))
            if cursor.fetchone()[0] == 0:
                flash("El ID de dirección no existe.")
                return redirect(url_for('crear'))

        try:
            cursor.execute("""
                INSERT INTO Personas (nombre, ap_paterno, ap_materno, telefono, correo)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, ap_paterno, ap_materno, telefono, correo))
            conn.commit()
            flash("Entrada creada exitosamente.")
        except pyodbc.IntegrityError as e:
            flash(f"Error en la base de datos: {e}")
        except Exception as e:
            flash(f"Error inesperado: {e}")

        return redirect(url_for('index'))

    return render_template('crear.html')

@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        ap_paterno = request.form['ap_paterno']
        ap_materno = request.form['ap_materno']
        telefono = request.form['telefono']
        correo = request.form['correo']
        direccion_id = request.form.get('direccion_id')  # Asumimos que `direccion_id` es opcional

        # Verificar que todos los campos requeridos estén presentes
        if not all([nombre, ap_paterno, ap_materno, telefono, correo]):
            flash("Todos los campos son requeridos.")
            return redirect(url_for('actualizar', id=id))

        # Validar que el `telefono` contenga solo números y no tenga más de 10 dígitos
        if not telefono.isdigit() or len(telefono) > 10:
            flash("El teléfono debe contener solo números y no puede tener más de 10 dígitos.")
            return redirect(url_for('actualizar', id=id))

        # Validar que el `correo` tenga un formato válido
        if not is_valid_email(correo):
            flash("El correo electrónico no es válido.")
            return redirect(url_for('actualizar', id=id))

        # Verificar que el `direccion_id` sea opcional
        if direccion_id:
            cursor.execute("SELECT COUNT(*) FROM Direcciones WHERE id = ?", (direccion_id,))
            if cursor.fetchone()[0] == 0:
                flash("El ID de dirección no existe.")
                return redirect(url_for('actualizar', id=id))

        try:
            cursor.execute("""
                UPDATE Personas
                SET nombre = ?, ap_paterno = ?, ap_materno = ?, telefono = ?, correo = ?
                WHERE id = ?
            """, (nombre, ap_paterno, ap_materno, telefono, correo, id))
            conn.commit()
            flash("Entrada actualizada exitosamente.")
        except pyodbc.IntegrityError as e:
            flash(f"Error en la base de datos: {e}")
        except Exception as e:
            flash(f"Error inesperado: {e}")

        return redirect(url_for('index'))

    # Mostrar formulario para actualizar una persona
    cursor.execute("SELECT * FROM Personas WHERE id = ?", (id,))
    persona = cursor.fetchone()
    if not persona:
        flash("Persona no encontrada.")
        return redirect(url_for('index'))

    return render_template('actualizar.html', persona=persona)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    try:
        cursor.execute("DELETE FROM Personas WHERE id = ?", (id,))
        conn.commit()
        flash("Entrada eliminada exitosamente.")
    except pyodbc.IntegrityError as e:
        flash(f"Error en la base de datos: {e}")
    except Exception as e:
        flash(f"Error inesperado: {e}")

    return redirect(url_for('index'))

@app.route('/leer/<int:id>')
def leer(id):
    cursor.execute("SELECT * FROM Personas WHERE id = ?", (id,))
    persona = cursor.fetchone()

    if persona is None:
        flash('Entrada no encontrada.', 'danger')
        return redirect(url_for('index'))

    return render_template('leer.html', persona=persona)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
