from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    conn = get_db_connection()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        try:
            conn.execute('INSERT INTO usuarios (nombre) VALUES (?)', (nombre,))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('usuarios.html', error="⚠️ Ese usuario ya existe.", usuarios=[])
    
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/libros', methods=['GET', 'POST'])
def libros():
    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        conn.execute('INSERT INTO libros (titulo, autor, prestado) VALUES (?, ?, 0)', (titulo, autor))
        conn.commit()

    libros = conn.execute('SELECT * FROM libros').fetchall()
    conn.close()
    return render_template('libros.html', libros=libros)

@app.route('/prestamos', methods=['GET', 'POST'])
def prestamos():
    conn = get_db_connection()
    error = None

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']

        # Verifica si el libro ya está prestado
        libro = conn.execute('SELECT prestado FROM libros WHERE id = ?', (libro_id,)).fetchone()
        if libro and libro['prestado']:
            error = "⛔ El libro ya está prestado."
        else:
            conn.execute('UPDATE libros SET prestado = 1 WHERE id = ?', (libro_id,))
            conn.commit()

    # Cargar usuarios y libros disponibles
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    libros = conn.execute('SELECT * FROM libros WHERE prestado = 0').fetchall()
    conn.close()
    return render_template('prestamos.html', usuarios=usuarios, libros=libros, error=error)

@app.route('/devoluciones', methods=['GET', 'POST'])
def devoluciones():
    conn = get_db_connection()
    error = None
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']

        # Marcar el libro como disponible
        conn.execute('UPDATE libros SET prestado = 0 WHERE id = ?', (libro_id,))
        conn.commit()

    # Si un usuario fue seleccionado, cargar sus libros prestados
    usuario_id = request.args.get('usuario_id')
    libros = []

    if usuario_id:
        libros = conn.execute(
            'SELECT * FROM libros WHERE prestado = 1'
        ).fetchall()

    conn.close()
    return render_template('devoluciones.html', usuarios=usuarios, libros=libros, usuario_id=usuario_id)

@app.route('/historial', methods=['GET'])
def historial():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()

    usuario_id = request.args.get('usuario_id')
    libros = []

    if usuario_id:
        libros = conn.execute('''
            SELECT libros.titulo, libros.autor
            FROM libros
            WHERE libros.prestado = 1
        ''').fetchall()

    conn.close()
    return render_template('historial.html', usuarios=usuarios, libros=libros, usuario_id=usuario_id)

from flask import send_file
import openpyxl
from io import BytesIO

@app.route('/exportar-excel')
def exportar_excel():
    conn = get_db_connection()
    prestamos = conn.execute('''
        SELECT prestamos.*, usuarios.nombre AS usuario, libros.titulo AS libro
        FROM prestamos
        JOIN usuarios ON prestamos.usuario_id = usuarios.id
        JOIN libros ON prestamos.libro_id = libros.id
        ORDER BY fecha_prestamo DESC
    ''').fetchall()
    conn.close()

    # Crear libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Préstamos"

    # Escribir encabezados
    ws.append(["Usuario", "Libro", "Fecha préstamo", "Fecha devolución"])

    # Escribir filas
    for p in prestamos:
        ws.append([
            p["usuario"],
            p["libro"],
            p["fecha_prestamo"],
            p["fecha_devolucion"] or "En préstamo"
        ])

    # Guardar en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        download_name="historial_prestamos.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

import matplotlib.pyplot as plt
from io import BytesIO
import base64

@app.route('/estadisticas')
def estadisticas():
    conn = get_db_connection()
    data = conn.execute('''
        SELECT usuarios.nombre, COUNT(*) as cantidad
        FROM prestamos
        JOIN usuarios ON prestamos.usuario_id = usuarios.id
        GROUP BY usuarios.nombre
        ORDER BY cantidad DESC
    ''').fetchall()
    conn.close()

    # Preparar datos
    nombres = [row['nombre'] for row in data]
    cantidades = [row['cantidad'] for row in data]

    # Crear gráfico
    fig, ax = plt.subplots()
    ax.bar(nombres, cantidades, color='skyblue')
    ax.set_title('📊 Préstamos por Usuario')
    ax.set_xlabel('Usuario')
    ax.set_ylabel('Cantidad de libros')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Convertir gráfico a imagen base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()

    return render_template('estadisticas.html', imagen=imagen_base64)


if __name__ == '__main__':
    print("🔥 Iniciando servidor Flask...")
    app.run(debug=True)

