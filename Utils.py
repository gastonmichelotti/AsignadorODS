import numpy as np# Función para calcular la matriz de distancias Haversine
def matriz_distancias_haversine(repas, envios):
    # Extraer coordenadas
    lat1 = np.radians(np.array([repa['latitud'] for repa in repas]))[:, np.newaxis]
    lon1 = np.radians(np.array([repa['longitud'] for repa in repas]))[:, np.newaxis]
    lat2 = np.radians(np.array([envio['latitudOrigen'] for envio in envios]))[np.newaxis, :]
    lon2 = np.radians(np.array([envio['longitudOrigen'] for envio in envios]))[np.newaxis, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    R = 6371000  # Radio de la Tierra en metros
    distancia = R * c
    return distancia  # Retorna la matriz de distancias en metros