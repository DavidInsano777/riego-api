import mysql.connector

# Configuración (la misma que usas en app.py)
db_config = {
    'host':     'metro.proxy.rlwy.net',        # ejemplo: containers-us-west-89.railway.app
    'user':     'root',
    'password': 'gJbctkiVlTpCHtgGRbNbBbvMydTiCQMh',
    'database': 'railway',
    'port': 35484                    # o el que aparezca en Railway mysql://root:rEoFMvdjfXZtcnCmkVGGFbvEzsQgMUIm@shinkansen.proxy.rlwy.net:30825/railway
}

# Conexión y creación de tabla
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE lecturas2 (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            humedad INT NOT NULL,
            riego VARCHAR(20),
            fecha DATETIME
        );
    """)

    conn.commit()
    print("✅ Tabla creada correctamente.")

except Exception as e:
    print("❌ Error:", e)

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
