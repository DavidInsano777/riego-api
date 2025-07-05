from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import mysql.connector
import os
app = Flask(__name__)

# Configuración de conexión (pon aquí los datos de Railway)
db_config = {
    'host':     'shinkansen.proxy.rlwy.net',        # ejemplo: containers-us-west-89.railway.app
    'user':     'root',
    'password': 'rEoFMvdjfXZtcnCmkVGGFbvEzsQgMUIm',
    'database': 'railway',
    'port': 30825                    # o el que te aparezca en Railway mysql://root:rEoFMvdjfXZtcnCmkVGGFbvEzsQgMUIm@shinkansen.proxy.rlwy.net:30825/railway
}

# Ruta base para verificar que funciona
@app.route('/')
def home():
    return '✅ API de riego conectada a Railway'

# Ruta para recibir y guardar lecturas
@app.route('/lectura', methods=['POST'])
def recibir_lectura():
    try:
        data = request.get_json()
        
        # Validación básica
        if not all (k in data for k in ("humedad", "riego", "fecha")):
            return jsonify({"error": "Faltan campos"}), 400
        

        # Formato de fecha correcto
        try:
            fecha = datetime.fromisoformat(data['fecha']) - timedelta(hours=6)
        except:
            return jsonify({"error": "Formato de fecha inválido"}), 400

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
            "message": "✅ Lectura guardada en Railway",
            "datos": valores
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

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)