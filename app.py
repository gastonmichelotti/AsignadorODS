from flask import Flask, request, jsonify
from PMAsignador import asignar_repas_envios_simple

app = Flask(__name__)

@app.route('/asignar_repas', methods=['POST'])
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

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(port=5005)
