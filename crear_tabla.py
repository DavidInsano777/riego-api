import mysql.connector

# Configuración (la misma que usas en app.py)
db_config = {
    'host':     'metro.proxy.rlwy.net',        
    'user':     'root',
    'password': 'gJbctkiVlTpCHtgGRbNbBbvMydTiCQMh',
    'database': 'railway',
    'port': 30825               
}

# Conexión y creación de tabla
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE lecturas1 (
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
