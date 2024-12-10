from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # Importar funciones para manejar contraseñas de forma segura

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_llave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de la base de datos y migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelos de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)

    def set_password(self, contraseña):
        """Generar el hash de la contraseña"""
        self.contraseña = generate_password_hash(contraseña)

    def check_password(self, contraseña):
        """Verificar si la contraseña proporcionada coincide con el hash"""
        return check_password_hash(self.contraseña, contraseña)


class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'))
    qr_id = db.Column(db.Integer, db.ForeignKey('qr.id'))

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'))
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'))

class QR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'))
    qr_code = db.Column(db.String(255), unique=True, nullable=False)

# Rutas
@app.route('/')
def index():
    return render_template('index.html', title="Inicio")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Si el formulario se envía
        email = request.form['email']  # Obtener el correo ingresado
        contraseña = request.form['password']  # Obtener la contraseña ingresada

        # Buscar al usuario en la base de datos
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(contraseña):  # Usar el método para verificar la contraseña
            session['user_id'] = usuario.id  # Guardar el ID del usuario en la sesión
            session['user_name'] = usuario.nombre  # Guardar el nombre del usuario
            flash(f"¡Bienvenido, {usuario.nombre}!", "success")  # Mostrar mensaje de bienvenida
            return redirect(url_for('index'))  # Redirigir a la página de inicio
        else:
            flash("Correo o contraseña incorrectos", "danger")  # Mostrar error si son incorrectos

    return render_template('login.html', title="Iniciar Sesión")

@app.route('/logout')
def logout():
    session.clear()  # Limpiar los datos de la sesión
    flash("Has cerrado sesión exitosamente", "info")
    return redirect(url_for('index'))


@app.route('/registrar_asistencia', methods=['POST'])
def registrar_asistencia():
    qr_code = request.form['qr_code']
    estudiante_qr = QR.query.filter_by(qr_code=qr_code).first()
    if estudiante_qr:
        nueva_asistencia = Asistencia(
            fecha=datetime.utcnow(),
            estado='Presente',
            estudiante_id=estudiante_qr.estudiante_id,
            curso_id=1  # Cambiar según lógica de tu sistema
        )
        db.session.add(nueva_asistencia)
        db.session.commit()
        flash("Asistencia registrada correctamente", "success")
    else:
        flash("Código QR inválido", "danger")
    return redirect(url_for('index'))

# Crear la base de datos al inicio utilizando Flask signals
def create_tables():
    """Creación de las tablas de la base de datos si no existen."""
    with app.app_context():
        db.create_all()

# Ejecutar la creación de las tablas antes de arrancar el servidor
create_tables()

# Ejecución de la aplicación
if __name__ == "__main__":
    app.run(debug=True)

