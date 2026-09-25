import os
import psycopg2


# ==========================================
# CONEXIÓN A POSTGRESQL
# ==========================================

def obtener_conexion():

    # Obtener la URL de PostgreSQL de Render.
    # En la computadora local esta variable normalmente no existe.
    database_url = os.environ.get("DATABASE_URL")

    # Si existe DATABASE_URL, significa que estamos usando
    # la base de datos configurada para Render.
    if database_url:
        conexion = psycopg2.connect(database_url)

    # Si no existe DATABASE_URL, utilizar PostgreSQL local.
    else:
        conexion = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password=os.environ.get("POSTGRES_PASSWORD"),
            database="arte_mostacilla"
        )

    # Retornar la conexión para utilizarla en app.py
    return conexion