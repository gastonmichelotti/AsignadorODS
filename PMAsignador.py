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


def asignar_repas_envios_zonas(viajes, reservas, dist_max_v1, dist_max_v4):
    
    """
    Asigna repartidores a envíos basándose en zonas geográficas comunes entre viajes y reservas,
    con la restricción de no asignar viajes cuya distancia supere la distancia máxima para el idVehiculo.
    
    Parámetros:
      - viajes (list): Lista de diccionarios con info de los viajes.
      - reservas (list): Lista de diccionarios con info de los repartidores.
      - dist_max_v1 (float): Distancia máxima de asignación en metros para vehículo con id=1.
      - dist_max_v4 (float): Distancia máxima de asignación en metros para vehículo con id=4.

    Retorna:
      dict con:
        - "asignaciones": Lista de asignaciones (diccionarios con IdViaje, IdReserva, DistanciaPickeo, etc.).
        - "distancia_total_metros": Distancia total acumulada de todas las asignaciones.
        - "distancia_promedio_idvehiculo_1": Distancia promedio de las asignaciones para vehículo con id=1.
        - "distancia_promedio_idvehiculo_4": Distancia promedio de las asignaciones para vehículo con id=4.
        - "metricas_por_direccion": Métricas detalladas por cada idDireccion.
    """

    # 1. Estructuras para métricas
    resultado_final = {
        "asignaciones": [],
        "distancia_total_metros": 0,
        "distancia_promedio_idvehiculo_1": 0,
        "distancia_promedio_idvehiculo_4": 0,
        "metricas_por_direccion": {}
    }

    # 2. Diccionario para acumular métricas por dirección
    metricas_por_dir = defaultdict(lambda: {
        'distancia_total': 0,
        'suma_1': 0,
        'count_1': 0,
        'suma_4': 0,
        'count_4': 0
    })

    # 3. Agrupar viajes y reservas por idDireccion
    grupos_viajes = defaultdict(list)
    for viaje in viajes:
        grupos_viajes[viaje['idDireccion']].append(viaje)

    grupos_reservas = defaultdict(list)
    for reserva in reservas:
        grupos_reservas[reserva['idDireccion']].append(reserva)

    # 4. Procesar cada dirección en común
    direcciones_comunes = set(grupos_viajes.keys()) & set(grupos_reservas.keys())
    for id_dir in direcciones_comunes:
        sub_viajes = grupos_viajes[id_dir]
        sub_reservas = grupos_reservas[id_dir]

        # Calcular la matriz de distancias
        matriz = matriz_distancias_haversine(sub_reservas, sub_viajes)

        # Para cada par (reserva, viaje), si excede la distancia máxima, asignamos un costo grande
        for i, reserva in enumerate(sub_reservas):
            vehiculo = reserva['idVehiculo']
            for j, viaje in enumerate(sub_viajes):
                dist = matriz[i, j]
                
                # Determinar distancia máxima según el idVehiculo
                if vehiculo == 1:
                    dist_max = dist_max_v1
                elif vehiculo == 4:
                    dist_max = dist_max_v4
                else:
                    # Si se desconoce el vehículo, podrías decidir asignar sin restricción o poner un valor grande
                    dist_max = 999999999

                # Si excede la distancia máxima, penalizar con un valor grande
                if dist > dist_max:
                    matriz[i, j] = 999999999  # costo muy alto para evitar asignación

        # 5. Resolver la asignación con algoritmo húngaro
        row_ind, col_ind = linear_sum_assignment(matriz)

        # 6. Procesar las asignaciones reales (ignorando las "penalizadas")
        for i, j in zip(row_ind, col_ind):
            distancia = matriz[i, j]
            # Si la distancia es muy grande, significa que no se debe asignar.
            if distancia >= 999999999:
                # Se ignora esta asignación
                continue

            reserva = sub_reservas[i]
            viaje = sub_viajes[j]

            resultado_final["distancia_total_metros"] += distancia

            if reserva['idVehiculo'] == 1:
                metricas_por_dir[id_dir]['suma_1'] += distancia
                metricas_por_dir[id_dir]['count_1'] += 1
            elif reserva['idVehiculo'] == 4:
                metricas_por_dir[id_dir]['suma_4'] += distancia
                metricas_por_dir[id_dir]['count_4'] += 1

            metricas_por_dir[id_dir]['distancia_total'] += distancia

            # Añadir la asignación
            resultado_final["asignaciones"].append({
                "$id": f"{id_dir}-{len(resultado_final['asignaciones'])+1}",
                "IdViaje": viaje['id'],
                "IdReserva": reserva['id'],
                "DistanciaPickeo": round(distancia, 2),
                "Coeficiente": round(distancia, 2)
            })

    # 7. Calcular promedios globales
    total_1 = 0
    count_1 = 0
    total_4 = 0
    count_4 = 0

    for id_dir, metrics in metricas_por_dir.items():
        total_1 += metrics['suma_1']
        count_1 += metrics['count_1']
        total_4 += metrics['suma_4']
        count_4 += metrics['count_4']

    if count_1 > 0:
        resultado_final["distancia_promedio_idvehiculo_1"] = round(total_1 / count_1, 2)
    if count_4 > 0:
        resultado_final["distancia_promedio_idvehiculo_4"] = round(total_4 / count_4, 2)

    resultado_final["distancia_total_metros"] = round(resultado_final["distancia_total_metros"], 2)

    # 8. Calcular métricas por dirección
    resultado_final["metricas_por_direccion"] = {}
    for id_dir, metrics in metricas_por_dir.items():
        dist_total_dir = metrics['distancia_total']
        d1 = metrics['suma_1']
        c1 = metrics['count_1']
        d4 = metrics['suma_4']
        c4 = metrics['count_4']
        
        resultado_final["metricas_por_direccion"][id_dir] = {
            "distancia_total_metros": round(dist_total_dir, 2),
            "distancia_promedio_idvehiculo_1": round(d1 / c1, 2) if c1 > 0 else 0,
            "distancia_promedio_idvehiculo_4": round(d4 / c4, 2) if c4 > 0 else 0
        }

    return resultado_final