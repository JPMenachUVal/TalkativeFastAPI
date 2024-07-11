# Usa la imagen oficial de Python 3.9
FROM python:3.9

# Actualiza pip a la última versión
RUN pip install --upgrade pip

# Crea un directorio de trabajo
WORKDIR /usr/src/app

# Copia el archivo de requisitos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto que usa la aplicación
EXPOSE 8001

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
