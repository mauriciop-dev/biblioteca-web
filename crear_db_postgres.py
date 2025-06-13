from app import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS libros (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    prestado BOOLEAN DEFAULT FALSE
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS prestamos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    libro_id INTEGER REFERENCES libros(id),
    fecha_prestamo TIMESTAMP NOT NULL,
    fecha_devolucion TIMESTAMP
);
''')

conn.commit()
cur.close()
conn.close()
print("✅ Tablas creadas en PostgreSQL.")
