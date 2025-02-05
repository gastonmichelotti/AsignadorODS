from flask import Flask, request, jsonify
from PMAsignador import asignar_repas_envios_simple, asignar_repas_envios_zonas

app = Flask(__name__)

@app.route('/asignar_repas', methods=['POST'], endpoint='asignar_repas_endpoint')
def asignar_repas():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Extraer los parámetros de la solicitud
        viajes = data.get('viajes')
        reservas = data.get('reservas')
        
        # Validar que los parámetros no sean None
        if viajes is None or reservas is None:
            return jsonify({"error": "Faltan parámetros 'viajes' o 'reservas'"}), 400
        
        # Validar que los parámetros sean listas
        if not isinstance(viajes, list) or not isinstance(reservas, list):
            return jsonify({"error": "'viajes' y 'reservas' deben ser listas"}), 400
        
        # Llamar a la función
        resultado = asignar_repas_envios_simple(viajes, reservas)
        
        # Devolver el resultado como JSON
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/asignar_repas_zonas', methods=['POST'], endpoint='asignar_repas_zonas_endpoint')
def asignar_repas_zonas():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Extraer los parámetros de la solicitud
        viajes = data.get('viajes')
        reservas = data.get('reservas')
        
        # Los dos nuevos parámetros de distancia máxima
        dist_max_v1 = data.get('DistanciaMaximaVehiculo1')
        dist_max_v4 = data.get('DistanciaMaximaVehiculo4')
        dist_max_entrega_v4 = data.get('DistanciaMaximaEntregaVehiculo4')
        
        # Validar que los parámetros no sean None
        if viajes is None or reservas is None:
            return jsonify({"error": "Faltan parámetros 'viajes' o 'reservas'"}), 400
        if dist_max_v1 is None or dist_max_v4 is None:
            return jsonify({"error": "Faltan parámetros de distancia máxima para vehículo 1 o 4"}), 400
        
        # Validar que los parámetros sean listas
        if not isinstance(viajes, list) or not isinstance(reservas, list):
            return jsonify({"error": "'viajes' y 'reservas' deben ser listas"}), 400
        
        # Asegurarnos de que las distancias máximas vengan como números
        try:
            dist_max_v1 = float(dist_max_v1)
            dist_max_v4 = float(dist_max_v4)
            dist_max_entrega_v4 = float(dist_max_entrega_v4)
        except ValueError:
            return jsonify({"error": "DistanciaMaximaVehiculo1 y DistanciaMaximaVehiculo4 deben ser numéricos"}), 400
        
        # Llamar a la función con los nuevos parámetros
        resultado = asignar_repas_envios_zonas(viajes, reservas, dist_max_v1, dist_max_v4, dist_max_entrega_v4)
        
        # Devolver el resultado como JSON
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/asignar_repas_zonas_migrantes', methods=['POST'], endpoint='asignar_repas_zonas_migrantes_endpoint')
def asignar_repas_zonas_migrantes():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        # Extraer los parámetros de la solicitud
        viajes = data.get('viajes')
        reservas = data.get('reservas')
        
        # Los dos nuevos parámetros de distancia máxima
        dist_max_v1 = data.get('DistanciaMaximaVehiculo1')
        dist_max_v4 = data.get('DistanciaMaximaVehiculo4')
        
        # Validar que los parámetros no sean None
        if viajes is None or reservas is None:
            return jsonify({"error": "Faltan parámetros 'viajes' o 'reservas'"}), 400
        if dist_max_v1 is None or dist_max_v4 is None:
            return jsonify({"error": "Faltan parámetros de distancia máxima para vehículo 1 o 4"}), 400
        
        # Validar que los parámetros sean listas
        if not isinstance(viajes, list) or not isinstance(reservas, list):
            return jsonify({"error": "'viajes' y 'reservas' deben ser listas"}), 400
        
        # Asegurarnos de que las distancias máximas vengan como números
        try:
            dist_max_v1 = float(dist_max_v1)
            dist_max_v4 = float(dist_max_v4)
        except ValueError:
            return jsonify({"error": "DistanciaMaximaVehiculo1 y DistanciaMaximaVehiculo4 deben ser numéricos"}), 400
        
        # Llamar a la función con los nuevos parámetros
        resultado = asignar_repas_envios_zonas(viajes, reservas, dist_max_v1, dist_max_v4)
        
        # Devolver el resultado como JSON
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5005)