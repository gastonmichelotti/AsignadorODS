import numpy as np
from datetime import datetime

def matriz_distancias_haversine(repas, envios, tiempo_actual, return_both=False):
    # Extraer coordenadas y calcular la matriz de distancias en línea recta.
    lat1 = np.radians(np.array([repa['latitud'] for repa in repas]))[:, np.newaxis]
    lon1 = np.radians(np.array([repa['longitud'] for repa in repas]))[:, np.newaxis]
    lat2 = np.radians(np.array([envio['latitudOrigen'] for envio in envios]))[np.newaxis, :]
    lon2 = np.radians(np.array([envio['longitudOrigen'] for envio in envios]))[np.newaxis, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    R = 6371000  # Radio de la Tierra en metros
    distancias_puras = R * c

    # Calcular antigüedad (en minutos) de cada envío usando el tiempo_actual.
    antiguedades = np.array([
        (tiempo_actual - datetime.fromisoformat(envio['fechaProcesamiento'])).total_seconds() / 60.0
        for envio in envios
    ])[np.newaxis, :]
    antiguedades = np.maximum(antiguedades, 0.1)  # Evitar división por cero

    # Calcular la matriz de coeficientes: distancia / antigüedad.
    coeficientes = distancias_puras / antiguedades

    if return_both:
        return distancias_puras, coeficientes
    else:
        return coeficientes