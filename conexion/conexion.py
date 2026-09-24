import os
import psycopg2


# ==========================================
# CONEXIÓN A POSTGRESQL
# ==========================================

def obtener_conexion():

    # Crear la conexión con la base de datos PostgreSQL
    conexion = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password=os.environ.get("POSTGRES_PASSWORD"),
        database="arte_mostacilla"
    )

    # Retornar la conexión para utilizarla en app.py
    return conexion