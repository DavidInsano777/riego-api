from flask import Flask, request, jsonify, render_template
from datetime import datetime
import mysql.connector
import os
import pytz
from dotenv import load_dotenv
from contextlib import closing

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración mejorada de la base de datos
db_config = {
    'host': os.getenv('DB_HOST', 'metro.proxy.rlwy.net'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'gJbctkiVlTpCHtgGRbNbBbvMydTiCQMh'),
    'database': os.getenv('DB_NAME', 'railway'),
    'port': int(os.getenv('DB_PORT', 35484)),
    'pool_name': 'webapp_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        app.logger.error(f"Error de conexión a la base de datos: {err}")
        raise

# Ruta principal
@app.route('/')
def home():
    return 'API de riego automatizado - Conectado a Railway'

# Ruta para recibir datos del sensor
@app.route('/lectura', methods=['POST'])
def recibir_lectura():
    try:
        data = request.get_json()

        # Validación robusta de datos
        if not data or 'humedad' not in data or 'riego' not in data:
            return jsonify({"error": "Datos incompletos. Se requieren 'humedad' y 'riego'"}), 400

        # Validar tipos de datos
        if not isinstance(data['humedad'], (int, float)) or not isinstance(data['riego'], bool):
            return jsonify({"error": "Tipos de datos incorrectos"}), 400

        # Manejo de zona horaria
        utc_now = datetime.now(pytz.utc)
        cdmx_time = utc_now.astimezone(pytz.timezone("America/Mexico_City"))
        fecha = cdmx_time.replace(tzinfo=None)

        with closing(get_db_connection()) as conn:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO lecturas3 (humedad, riego, fecha) 
                VALUES (%s, %s, %s)
                """
                valores = (data['humedad'], data['riego'], fecha)
                cursor.execute(query, valores)
                conn.commit()

        return jsonify({
            "message": "Lectura registrada exitosamente",
            "registro": {
                "humedad": data['humedad'],
                "riego": data['riego'],
                "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S")
            }
        }), 201

    except mysql.connector.Error as db_err:
        app.logger.error(f"Error de base de datos: {db_err}")
        return jsonify({"error": "Error al guardar en la base de datos"}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Ruta para obtener lecturas en JSON
@app.route('/lecturas_json', methods=['GET'])
def obtener_lecturas_json():
    try:
        with closing(get_db_connection()) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id, humedad, riego, 
                           DATE_FORMAT(fecha, '%%Y-%%m-%%d %%H:%%i:%%S') as fecha 
                    FROM lecturas3
                    ORDER BY fecha DESC 
                    LIMIT 50
                """)
                resultados = cursor.fetchall()

        # Convertir el campo 'riego' de tinyint(1) a booleano
        for lectura in resultados:
            lectura['riego'] = bool(lectura['riego'])

        return jsonify(resultados), 200

    except Exception as e:
        app.logger.error(f"Error al obtener lecturas: {e}")
        return jsonify({"error": "No se pudieron obtener las lecturas"}), 500

# Ruta para mostrar la interfaz web
@app.route('/lecturas', methods=['GET'])
def obtener_lecturas():
    try:
        with closing(get_db_connection()) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id, humedad, riego, fecha 
                    FROM lecturas3
                    ORDER BY fecha DESC 
                    LIMIT 50
                """)
                resultados = cursor.fetchall()

                # Convertir el campo 'riego' de tinyint(1) a booleano
                for lectura in resultados:
                    lectura['riego'] = bool(lectura['riego']) if lectura['riego'] in (1, True) else False


        return render_template('lecturas.html', 
                            lecturas=resultados,
                            now=datetime.now())

    except Exception as e:
        app.logger.error(f"Error al renderizar lecturas: {e}")
        return """
        <h1>Error</h1>
        <p>No se pudieron cargar las lecturas</p>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="#f44336">
            <path d="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16"/>
        </svg>
        """, 500

# Ruta para eliminar una lectura
@app.route('/lectura/<int:id>', methods=['DELETE'])
def eliminar_lectura(id):
    try:
        with closing(get_db_connection()) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM lecturas3 WHERE id = %s", (id,))
                if cursor.rowcount == 0:
                    return jsonify({"error": "Lectura no encontrada"}), 404
                conn.commit()

        return jsonify({"message": "✅ Lectura eliminada correctamente"}), 200

    except mysql.connector.Error as db_err:
        app.logger.error(f"Error al eliminar: {db_err}")
        return jsonify({"error": "Error al eliminar la lectura"}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado al eliminar: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)