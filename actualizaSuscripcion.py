from flask import Flask, request, jsonify
from flask_caching import Cache
import pymongo

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def conectar_atlas():
    uri = "mongodb+srv://topicos2023:app1234@cluster0.dmuqbzs.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    print("Conexión exitosa a MongoDB")
    return client

def actualizar_tipo_suscripcion(user, password, nuevo_tipo):
    client = conectar_atlas()

    db = client.app1
    collection = db.users

    result = collection.update_one({"user": user, "password": password}, {"$set": {"subscription": nuevo_tipo}})
    print("Result Modified Count:", result.modified_count)
    
    cache.delete((user, password))

    client.close()

    return result.modified_count > 0

@app.route('/actualizar_suscripcion', methods=['PUT'])
def actualizar_suscripcion():
    try:
        data = request.get_json()

        user = data.get('user')
        password = data.get('password')
        nuevo_tipo = data.get('tipo_suscripcion')

        if user and password and nuevo_tipo:
            if actualizar_tipo_suscripcion(user, password, nuevo_tipo):
                return jsonify({"message": "Tipo de suscripción actualizado correctamente"}), 200
            else:
                return jsonify({"message": "No se pudo actualizar el tipo de suscripción"}), 404
        else:
            return jsonify({"message": "Se requieren user, password y tipo_suscripcion"}), 400

    except Exception as e:
        print(f"Error en actualizar_suscripcion: {str(e)}")
        return jsonify({"message": "Ocurrió un error al procesar la solicitud"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5005)
    