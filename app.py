from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import mysql.connector
import os
import pytz
app = Flask(__name__)

# Configuración de conexión a la base de datos MySQL en Railway
db_config = {
    'host':     'metro.proxy.rlwy.net',        
    'user':     'root',
    'password': 'gJbctkiVlTpCHtgGRbNbBbvMydTiCQMh',
    'database': 'railway',
    'port': 35484               
}

# Ruta base para verificar que funciona
@app.route('/')
def home():
    return 'API de riego conectada a Railway'

# Ruta para recibir y guardar lecturas
@app.route('/lectura', methods=['POST'])
def recibir_lectura():
    try:
        data = request.get_json()

        # Validación: humedad y riego son obligatorios
        if not all(k in data for k in ("humedad", "riego")):
            return jsonify({"error": "Faltan campos"}), 400

        # Obtener hora actual en UTC y convertirla a CDMX
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        cdmx_time = utc_now.astimezone(pytz.timezone("America/Mexico_City"))

        # Quitar zona horaria para evitar desajustes al guardar en MySQL
        fecha = cdmx_time.replace(tzinfo=None)

        # Conexión a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "INSERT INTO lecturas2 (humedad, riego, fecha) VALUES (%s, %s, %s)"
        valores = (data['humedad'], data['riego'], fecha)
        cursor.execute(query, valores)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Lectura registrada exitosamente",
            "registro": {
                "humedad": data['humedad'],
                "riego": data['riego'],
                "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/lecturas', methods=['GET'])
def obtener_lecturas():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM lecturas2 ORDER BY fecha DESC LIMIT 50")
        resultados = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('lecturas.html', lecturas=resultados)

    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

