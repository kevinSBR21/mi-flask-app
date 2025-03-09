from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import urllib

app = Flask(__name__)
CORS(app)

# Configuración de la conexión a SQL Server usando pyodbc
params = urllib.parse.quote_plus(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=kilat1\SQLEXPRESS;"
    r"DATABASE=Edu_Nauta;"
    r"Trusted_Connection=yes;"
    r"TrustServerCertificate=yes;"
)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Ruta de registro
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 1. Validar que se envíen datos
    if not username or not password:
        return jsonify({'error': 'Faltan datos'}), 400

    # 2. Verificar si el usuario ya existe
    usuario_existente = Usuario.query.filter_by(username=username).first()
    if usuario_existente:
        return jsonify({'error': 'El usuario ya existe'}), 400

    # 3. Crear el usuario y guardarlo en la base de datos
    #    (en un entorno real, aquí deberías encriptar la contraseña)
    nuevo_usuario = Usuario(username=username, password=password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado con éxito'}), 201

# Ruta de login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Faltan datos'}), 400

    # Buscar el usuario en la BD
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Verificar la contraseña (en producción, usar hashing)
    if usuario.password != password:
        return jsonify({'error': 'Contraseña incorrecta'}), 401

    return jsonify({'message': 'Inicio de sesión exitoso'}), 200

if __name__ == '__main__':
    app.run(debug=True)
