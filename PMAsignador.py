import numpy as np
from scipy.optimize import linear_sum_assignment
import json
from collections import defaultdict
from Utils import matriz_distancias_haversine

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


def asignar_repas_envios_zonas(viajes, reservas):
    """
    Asigna repartidores a envíos basándose en zonas geográficas comunes entre viajes y reservas.

    Parámetros:
    viajes (list): Lista de diccionarios que representan los viajes, cada uno con información como id, idDireccion, latitudOrigen, longitudOrigen, etc.
    reservas (list): Lista de diccionarios que representan las reservas, cada uno con información como id, idDireccion, latitud, longitud, etc.

    Retorna:
    dict: Un diccionario que contiene:
        - "asignaciones": Lista de asignaciones realizadas.
        - "distancia_total_metros": Distancia total acumulada de todas las asignaciones.
        - "distancia_promedio_idvehiculo_1": Distancia promedio de las asignaciones para el vehículo con id 1.
        - "distancia_promedio_idvehiculo_4": Distancia promedio de las asignaciones para el vehículo con id 4.
    """

    # Crear diccionarios de grupos
    grupos_viajes = defaultdict(list)
    grupos_reservas = defaultdict(list)
    
    for viaje in viajes:
        grupos_viajes[viaje['idDireccion']].append(viaje)
    
    for reserva in reservas:
        grupos_reservas[reserva['idDireccion']].append(reserva)
    
    # 2. Procesar cada grupo común
    resultado_final = {
        "asignaciones": [],
        "distancia_total_metros": 0,
        "distancia_promedio_idvehiculo_1": 0,
        "distancia_promedio_idvehiculo_4": 0
    }
    
    # Acumuladores para promedios
    total_dist_1 = 0
    count_1 = 0
    total_dist_4 = 0
    count_4 = 0
    
    # Iterar sobre direcciones comunes
    for id_dir in set(grupos_viajes.keys()) & set(grupos_reservas.keys()):
        # Obtener subconjuntos
        sub_viajes = grupos_viajes[id_dir]
        sub_reservas = grupos_reservas[id_dir]
        
        # 3. Ejecutar asignación para el subgrupo
        matriz_distancias = matriz_distancias_haversine(sub_reservas, sub_viajes)
        filas_ind, columnas_ind = linear_sum_assignment(matriz_distancias)
        
        # Procesar asignaciones (similar al código original)
        for idx in range(min(len(filas_ind), len(columnas_ind))):
            i = filas_ind[idx]
            j = columnas_ind[idx]
            distancia = float(matriz_distancias[i, j])
            repa = sub_reservas[i]
            viaje = sub_viajes[j]
            
            # Acumular en resultado final
            resultado_final["asignaciones"].append({
                "$id": f"{id_dir}-{idx}",
                "IdViaje": viaje['id'],
                "IdReserva": repa['id'],
                "IdDireccion": viaje['idDireccion'],
                "DistanciaPickeo": round(distancia, 2),
                "Coeficiente": round(distancia, 2)
            })
            
            # Acumular distancias
            resultado_final["distancia_total_metros"] += distancia
            
            # Acumular para promedios
            if repa['idVehiculo'] == 1:
                total_dist_1 += distancia
                count_1 += 1
            elif repa['idVehiculo'] == 4:
                total_dist_4 += distancia
                count_4 += 1
    
    # 4. Calcular promedios finales
    resultado_final["distancia_total_metros"] = round(resultado_final["distancia_total_metros"], 2)
    
    if count_1 > 0:
        resultado_final["distancia_promedio_idvehiculo_1"] = round(total_dist_1 / count_1, 2)
    if count_4 > 0:
        resultado_final["distancia_promedio_idvehiculo_4"] = round(total_dist_4 / count_4, 2)
    
    return resultado_final