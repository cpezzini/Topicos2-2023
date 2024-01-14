from flask import Flask, request, jsonify
from flask_caching import Cache
import pymongo
import threading
import time

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def conectar_atlas():
    uri = "mongodb+srv://topicos2023:app1234@cluster0.dmuqbzs.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    return client

@cache.memoize(timeout=180)
def obtener_tipo_suscripcion(user, password):
    cached_result = cache.get((user, password))
    if cached_result is not None:
        return cached_result

    client = conectar_atlas()

    db = client.app1
    collection = db.users

    resultado = collection.find_one({"user": user, "password": password})

    if resultado:
        tipo_suscripcion = resultado.get("subscription", "Sin suscripción")
        cache.set((user, password), tipo_suscripcion)
        return tipo_suscripcion
    else:
        return None  

    client.close()

contadores_consultas = {}

def reiniciar_contador():
    while True:
        time.sleep(60)  
        contadores_consultas.clear()  
        cache.clear()  

threading.Thread(target=reiniciar_contador, daemon=True).start()

@app.route('/obtener_suscripcion/<user>/<password>', methods=['GET'])
def obtener_suscripcion(user, password):
    try:
        tipo_suscripcion = obtener_tipo_suscripcion(user, password)

        if tipo_suscripcion is not None:
            limite_consultas = 0
            if tipo_suscripcion == "Premium":
                limite_consultas = 50
            elif tipo_suscripcion == "Freemium":
                limite_consultas = 5

            contador_actual = contadores_consultas.get((user, password), 0)

            if contador_actual < limite_consultas:
                contadores_consultas[(user, password)] = contador_actual + 1

                return jsonify({"tipo_suscripcion": tipo_suscripcion}), 200
            else:
                return jsonify({"message": f"Se ha alcanzado el límite de consultas para {user}/{password}"}), 429
        else:
            return jsonify({"message": f"Usuario no encontrado"}), 404

    except Exception as e:
        print(f"Error en obtener_suscripcion: {str(e)}")
        return "Ocurrió un error al procesar la solicitud"

if __name__ == "__main__":
    app.run(debug=True, port=5001)
