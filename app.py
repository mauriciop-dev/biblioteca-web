from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import psycopg2
import psycopg2.extras
import openpyxl
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def crear_tablas_si_no_existen():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE
        );

        CREATE TABLE IF NOT EXISTS libros (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200),
            autor VARCHAR(100),
            prestado BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS prestamos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            libro_id INTEGER REFERENCES libros(id),
            fecha_prestamo TIMESTAMP,
            fecha_devolucion TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        try:
            cur.execute('INSERT INTO usuarios (nombre) VALUES (%s)', (nombre,))
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            cur.close()
            conn.close()
            return render_template('usuarios.html', error="⚠️ Ese usuario ya existe.", usuarios=[])

    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/libros', methods=['GET', 'POST'])
def libros():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        cur.execute('INSERT INTO libros (titulo, autor, prestado) VALUES (%s, %s, %s)', (titulo, autor, False))
        conn.commit()

    cur.execute('SELECT * FROM libros')
    libros = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('libros.html', libros=libros)

@app.route('/prestamos', methods=['GET', 'POST'])
def prestamos():
    conn = get_db_connection()
    cur = conn.cursor()
    error = None

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']

        cur.execute('SELECT prestado FROM libros WHERE id = %s', (libro_id,))
        libro = cur.fetchone()
        if libro and libro['prestado']:
            error = "⛔ El libro ya está prestado."
        else:
            cur.execute('UPDATE libros SET prestado = TRUE WHERE id = %s', (libro_id,))
            cur.execute('INSERT INTO prestamos (usuario_id, libro_id, fecha_prestamo) VALUES (%s, %s, %s)',
                        (usuario_id, libro_id, datetime.now()))
            conn.commit()

    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()
    cur.execute('SELECT * FROM libros WHERE prestado = FALSE')
    libros = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('prestamos.html', usuarios=usuarios, libros=libros, error=error)

@app.route('/devoluciones', methods=['GET', 'POST'])
def devoluciones():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()

    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        libro_id = request.form['libro_id']
        cur.execute('UPDATE libros SET prestado = FALSE WHERE id = %s', (libro_id,))
        cur.execute('UPDATE prestamos SET fecha_devolucion = %s WHERE libro_id = %s AND usuario_id = %s AND fecha_devolucion IS NULL',
                    (datetime.now(), libro_id, usuario_id))
        conn.commit()

    usuario_id = request.args.get('usuario_id')
    libros = []
    if usuario_id:
        cur.execute('SELECT * FROM libros WHERE prestado = TRUE')
        libros = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('devoluciones.html', usuarios=usuarios, libros=libros, usuario_id=usuario_id)

@app.route('/historial')
def historial():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()

    usuario_id = request.args.get('usuario_id')
    libros = []
    if usuario_id:
        cur.execute('''
        SELECT libros.titulo, libros.autor
        FROM prestamos
        JOIN libros ON prestamos.libro_id = libros.id
        WHERE prestamos.usuario_id = %s AND prestamos.fecha_devolucion IS NULL
    ''', (usuario_id,))
    libros = cur.fetchall()


    cur.close()
    conn.close()
    return render_template('historial.html', usuarios=usuarios, libros=libros, usuario_id=usuario_id)

@app.route('/exportar-excel')
def exportar_excel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT prestamos.*, usuarios.nombre AS usuario, libros.titulo AS libro
        FROM prestamos
        JOIN usuarios ON prestamos.usuario_id = usuarios.id
        JOIN libros ON prestamos.libro_id = libros.id
        ORDER BY fecha_prestamo DESC
    ''')
    prestamos = cur.fetchall()
    cur.close()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Préstamos"
    ws.append(["Usuario", "Libro", "Fecha préstamo", "Fecha devolución"])
    for p in prestamos:
        ws.append([
            p["usuario"],
            p["libro"],
            p["fecha_prestamo"],
            p["fecha_devolucion"] or "En préstamo"
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        download_name="historial_prestamos.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/estadisticas')
def estadisticas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT usuarios.nombre, COUNT(*) as cantidad
        FROM prestamos
        JOIN usuarios ON prestamos.usuario_id = usuarios.id
        GROUP BY usuarios.nombre
        ORDER BY cantidad DESC
    ''')
    data = cur.fetchall()
    cur.close()
    conn.close()

    if not data:
        return render_template('estadisticas.html', imagen=None, mensaje="📭 No hay datos para mostrar estadísticas.")

    nombres = [row['nombre'] for row in data]
    cantidades = [row['cantidad'] for row in data]

    fig, ax = plt.subplots()
    ax.bar(nombres, cantidades, color='skyblue')
    ax.set_title('📊 Préstamos por Usuario')
    ax.set_xlabel('Usuario')
    ax.set_ylabel('Cantidad de libros')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return render_template('estadisticas.html', imagen=img, mensaje=None)

crear_tablas_si_no_existen()

if __name__ == '__main__':
    print("🛠️ Tablas verificadas. 🔥 Iniciando servidor Flask...")
    app.run(debug=True)

