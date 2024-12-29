FROM python:3.9-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el código fuente de tu bot
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar el bot
CMD ["python", "main.py"]
