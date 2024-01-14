from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

uri = "mongodb+srv://topicos2023:app1234@cluster0.dmuqbzs.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client.app1
bitacora_collection = db.bitacora

@app.route('/bitacora', methods=['POST'])
def otro_servicio():
    try:
        data = request.get_json()

        bitacora_entry = {
            "datos_user": data.get('datos_user'),
            "datos_riesgo_cardiaco": data.get('datos_riesgo_cardiaco'),
            "respuesta_riesgo_cardiaco": data.get('respuesta_riesgo_cardiaco'),
            "processing_time": data.get('processing_time'),
            "timestamp": datetime.datetime.now()
        }

        result = bitacora_collection.insert_one(bitacora_entry)

        if result.inserted_id:
            return jsonify({"message": "Registro de bitácora exitoso"}), 200
        else:
            return jsonify({"message": "Error al registrar en la bitácora"}), 500

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='localhost', port=5003, debug=True)