📚 Biblioteca Web – Flask + SQLite
Una aplicación web para gestionar usuarios, libros y préstamos en una biblioteca. Desarrollada con Python, Flask y SQLite.

🚀 Características
Registro y eliminación de usuarios 👤
Registro y eliminación de libros 📚
Préstamos y devoluciones 🔄
Historial completo de préstamos 🕘
Estadísticas gráficas 📊
Exportación a Excel 📥

🛠️ Tecnologías
Python 3.x
Flask
SQLite3
Matplotlib
Openpyxl
HTML/CSS (plantillas Jinja2)

📦 Requisitos
Instala dependencias con: pip install -r requirements.txt

▶️ Ejecutar localmente
python app.py
Luego visita:
http://127.0.0.1:5000

🌐 Despliegue en Render
Subir este repositorio a GitHub.
Crear un servicio en Render.com.
Asegurarse de tener:
requirements.txt
Procfile con: web: gunicorn app:app

Deploy automático o manual desde la interfaz.

📁 Estructura del proyecto

biblioteca_web/
├── app.py
├── crear_db.py
├── requirements.txt
├── Procfile
├── db.sqlite3
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   ├── usuarios.html
│   ├── libros.html
│   ├── prestamos.html
│   ├── devoluciones.html
│   ├── historial.html
│   ├── historial_completo.html
│   └── estadisticas.html

📬 Contacto

Desarrollado por mauriciop-dev
¡Colaboraciones, sugerencias y estrellas ⭐ son bienvenidas!