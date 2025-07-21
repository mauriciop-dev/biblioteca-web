# Usa una imagen oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto que usará la app
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "app.py"]
