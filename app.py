import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv

from db import get_connection
from validators import validar_registro, validar_login, validar_contacto
from security import verificar_password
from email_service import enviar_correo_contacto
from models import Registro

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_temporal_desarrollo")

# supports_credentials=True permite trabajar con cookies/sesiones desde el frontend.
# En producción conviene restringir origins al dominio real del frontend.
CORS(app, supports_credentials=True)


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "Backend Flask activo",
        "proyecto": "Plantilla genérica de negocio"
    }), 200



# REGISTROS PRINCIPALES DEL NEGOCIO
@app.route("/registros", methods=["GET"])
def obtener_registros():
    """Obtiene todos los registros principales del negocio."""
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM registros")
    registros = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(registros), 200

@app.route("/registros/<int:id>", methods=["GET"])
def obtener_registro(id):
    """Obtiene un registro por ID."""
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

   # cursor.execute("SELECT * FROM registros WHERE id = %s", (id,))
    cursor.execute("SELECT id, nombre, categoria, descripcion, precio, activo, destacado FROM registros")
    registro = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not registro:
        return jsonify({"mensaje": "Registro no encontrado"}), 404

    return jsonify(registro), 200

@app.route("/registros", methods=["POST"])
def agregar_registro():
    """Recibe datos desde Vue y agrega un registro en MariaDB."""
    data = request.json

    errores = validar_registro(data)
    if errores:
        return jsonify({"errores": errores}), 400

    conexion = get_connection()
    cursor = conexion.cursor()

    sql = """
        INSERT INTO registros (nombre, categoria, descripcion, precio, activo, destacado)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    valores = (
        data.get("nombre"),
        data.get("categoria"),
        data.get("descripcion"),
        float(data.get("precio", 0)),
        bool(data.get("activo", 1)),
        bool(data.get("destacado", 0))
    )

    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Registro agregado correctamente",
        "id": nuevo_id
    }), 201


@app.route("/registros/<int:id>", methods=["PUT"])
def actualizar_registro(id):
    """Actualiza un registro existente."""
    data = request.json

    errores = validar_registro(data)
    if errores:
        return jsonify({"errores": errores}), 400

    conexion = get_connection()
    cursor = conexion.cursor()

    sql = """
        UPDATE registros
        SET nombre = %s, categoria = %s, descripcion = %s, precio = %s, activo = %s, destacado = %s
        WHERE id = %s
    """

    valores = (
        data.get("nombre"),
        data.get("categoria"),
        data.get("descripcion"),
        float(data.get("precio", 0)),
        bool(data.get("activo", True)),
        bool(data.get("destacado", False)),
        id
    )

    cursor.execute(sql, valores)
    conexion.commit()
    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    if filas_afectadas == 0:
        return jsonify({"mensaje": "Registro no encontrado"}), 404

    return jsonify({"mensaje": "Registro actualizado correctamente"}), 200


# @app.route("/registros/<int:id>", methods=["DELETE"])
# def eliminar_registro(id):
#     """Elimina un registro por ID."""
#     conexion = get_connection()
#     cursor = conexion.cursor()

#     cursor.execute("DELETE FROM registros WHERE id = %s", (id,))
#     conexion.commit()
#     filas_afectadas = cursor.rowcount

#     cursor.close()
#     conexion.close()

#     if filas_afectadas == 0:
#         return jsonify({"mensaje": "Registro no encontrado"}), 404

#     return jsonify({"mensaje": "Registro eliminado correctamente"}), 200

@app.route("/registros/<int:id>/desactivar", methods=["PUT"])
def desactivar_registro(id):
    """No elimina el registro; solo cambia activo a 0."""
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute( "UPDATE registros SET activo = 0 WHERE id = %s", (id,) )

    conexion.commit()
    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    if filas_afectadas == 0:
        return jsonify({"mensaje": "Registro no encontrado"}), 404

    return jsonify({"mensaje": "Registro desactivado correctamente"}), 200


# LOGIN Y SESIÓN

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    errores = validar_login(data)
    if errores:
        return jsonify({"errores": errores}), 400

    correo = data.get("correo")
    password = data.get("password")

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    if not verificar_password(password, usuario["password"]):
        return jsonify({"mensaje": "Contraseña incorrecta"}), 401

    session["usuario_id"] = usuario["id"]
    session["nombreUsuario"] = usuario["nombre"]
    session["correo"] = usuario["correo"]
    session["autenticado"] = True

    return jsonify({
        "mensaje": "Sesión iniciada correctamente",
        "sesion": {
            "nombreUsuario": usuario["nombre"],
            "correo": usuario["correo"],
            "autenticado": True
        }
    }), 200


@app.route("/sesion", methods=["GET"])
def obtener_sesion():
    if session.get("autenticado"):
        return jsonify({
            "nombreUsuario": session.get("nombreUsuario"),
            "correo": session.get("correo"),
            "autenticado": True
        }), 200

    return jsonify({
        "nombreUsuario": "Invitado",
        "correo": None,
        "autenticado": False
    }), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200



# CONTACTO / CORREO
@app.route("/contacto", methods=["POST"])
def contacto():
    data = request.json

    errores = validar_contacto(data)
    if errores:
        return jsonify({"errores": errores}), 400

    enviar_correo_contacto(
        data.get("nombre"),
        data.get("correo"),
        data.get("mensaje")
    )

    return jsonify({"mensaje": "Correo enviado correctamente"}), 200


if __name__ == "__main__":
    app.run(debug=True)
