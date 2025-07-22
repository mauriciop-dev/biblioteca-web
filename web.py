# web.py

from flask import Flask, request, jsonify
from app import Library, User, Book  # Asegúrate que estas clases estén exportadas desde app.py

app = Flask(__name__)
biblioteca = Library("Biblioteca Virtual ProDig")
biblioteca.cargar_datos()


@app.route("/")
def inicio():
    return "🚀 Bienvenido a la Biblioteca Virtual Web"


@app.route("/libros", methods=["GET"])
def obtener_libros():
    libros = [libro.__dict__ for libro in biblioteca.libros_disponibles]
    return jsonify(libros)


@app.route("/usuarios", methods=["GET"])
def obtener_usuarios():
    usuarios = [usuario.__dict__ for usuario in biblioteca.usuarios]
    return jsonify(usuarios)


@app.route("/libros", methods=["POST"])
def agregar_libro():
    datos = request.json
    titulo = datos.get("titulo")
    autor = datos.get("autor")
    libro = Book(titulo, autor)
    biblioteca.agregar_libro(libro)
    biblioteca.guardar_datos()
    return jsonify({"mensaje": "📚 Libro agregado exitosamente"})


@app.route("/usuarios", methods=["POST"])
def registrar_usuario():
    datos = request.json
    nombre = datos.get("nombre")
    usuario = User(nombre)
    biblioteca.registrar_usuario(usuario)
    biblioteca.guardar_datos()
    return jsonify({"mensaje": f"👤 Usuario '{nombre}' registrado"})


@app.route("/prestamo", methods=["POST"])
def prestar_libro():
    datos = request.json
    usuario = datos.get("usuario")
    titulo = datos.get("titulo")
    biblioteca.prestar_libro(usuario, titulo)
    biblioteca.guardar_datos()
    return jsonify({"mensaje": f"✅ Libro '{titulo}' prestado a '{usuario}'"})


@app.route("/devolucion", methods=["POST"])
def devolver_libro():
    datos = request.json
    usuario = datos.get("usuario")
    titulo = datos.get("titulo")
    biblioteca.devolver_libro(usuario, titulo)
    biblioteca.guardar_datos()
    return jsonify({"mensaje": f"🔁 Libro '{titulo}' devuelto por '{usuario}'"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
