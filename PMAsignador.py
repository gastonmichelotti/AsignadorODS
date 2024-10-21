def asignar_repas_envios_simple(viajes, reservas):
    
    """
    Asigna repartidores a envíos utilizando minimización de distancias geográficas.

    Parámetros:
    - viajes: Lista de diccionarios con la información de los envíos.
    - reservas: Lista de diccionarios con la información de los repartidores.

    Retorna:
    - asignaciones_json: Lista de diccionarios con las asignaciones realizadas en el formato especificado.
    - distancia_total_metros: Suma total de las distancias de todas las asignaciones en metros.
    - distancia_promedio_idvehiculo_1: Promedio de las distancias de asignación para idVehiculo = 1.
    - distancia_promedio_idvehiculo_4: Promedio de las distancias de asignación para idVehiculo = 4.
    """
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    import json

    # Función para calcular la matriz de distancias Haversine
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

    # Asignar IDs
    ids_repas = [reserva['id'] for reserva in reservas]
    ids_envios = [viaje['id'] for viaje in viajes]

    # Inicializar listas de asignaciones y sobrantes
    asignaciones_json = []
    sobrantes_repas = ids_repas.copy()
    sobrantes_envios = ids_envios.copy()

    distancia_total_metros = 0  # Para acumular la distancia total de las asignaciones en metros
    distancias_asignaciones = []  # Lista para almacenar las distancias de cada asignación

    # Listas para distancias por idVehiculo
    distancias_idvehiculo_1 = []
    distancias_idvehiculo_4 = []

    # Crear matriz de distancias
    matriz_distancias = matriz_distancias_haversine(reservas, viajes)

    # Resolver el problema de asignación utilizando el algoritmo húngaro
    filas_ind, columnas_ind = linear_sum_assignment(matriz_distancias)

    num_asignaciones = min(len(filas_ind), len(columnas_ind))

    # Acumular distancia total y realizar asignaciones
    for idx in range(num_asignaciones):
        i = filas_ind[idx]
        j = columnas_ind[idx]
        repa_id = ids_repas[i]
        envio_id = ids_envios[j]
        distancia = float(matriz_distancias[i, j])  # Convertir a tipo float
        repa = reservas[i]
        idVehiculo = repa['idVehiculo']

        # Crear el JSON de asignación en el formato solicitado
        asignaciones_json.append({
            "$id": str(idx + 1),  # Usamos 'idx + 1' para asignar un ID incremental
            "IdViaje": envio_id,
            "IdReserva": repa_id,
            "DistanciaPickeo": round(distancia, 2),
            "Coeficiente": round(distancia, 2)  # El coeficiente es igual a la distancia
        })

        distancia_total_metros += distancia
        distancias_asignaciones.append(distancia)

        # Acumular distancias por idVehiculo
        if idVehiculo == 1:
            distancias_idvehiculo_1.append(distancia)
        elif idVehiculo == 4:
            distancias_idvehiculo_4.append(distancia)

        # Remover asignados de los sobrantes
        if repa_id in sobrantes_repas:
            sobrantes_repas.remove(repa_id)
        if envio_id in sobrantes_envios:
            sobrantes_envios.remove(envio_id)

    total_asignaciones = len(asignaciones_json)

    # Calcular la distancia promedio total
    if total_asignaciones > 0:
        distancia_promedio_metros = distancia_total_metros / total_asignaciones
    else:
        distancia_promedio_metros = 0

    # Calcular la distancia promedio para idVehiculo = 1
    if distancias_idvehiculo_1:
        distancia_promedio_idvehiculo_1 = sum(distancias_idvehiculo_1) / len(distancias_idvehiculo_1)
    else:
        distancia_promedio_idvehiculo_1 = 0

    # Calcular la distancia promedio para idVehiculo = 4
    if distancias_idvehiculo_4:
        distancia_promedio_idvehiculo_4 = sum(distancias_idvehiculo_4) / len(distancias_idvehiculo_4)
    else:
        distancia_promedio_idvehiculo_4 = 0

    resultado = {
        "asignaciones": asignaciones_json,
        "distancia_total_metros": round(distancia_total_metros, 2),
        "distancia_promedio_idvehiculo_1": round(distancia_promedio_idvehiculo_1, 2),
        "distancia_promedio_idvehiculo_4": round(distancia_promedio_idvehiculo_4, 2)
    }
    return resultado