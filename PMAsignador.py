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


from collections import defaultdict
from scipy.optimize import linear_sum_assignment
import numpy as np

from collections import defaultdict
from scipy.optimize import linear_sum_assignment
import numpy as np

from collections import defaultdict
from scipy.optimize import linear_sum_assignment
import numpy as np

def asignar_repas_envios_zonas(viajes, reservas, dist_max_v1, dist_max_v4, dist_max_entrega_v4, tiempo_actual):
    """
    Asigna repartidores a envíos basándose en zonas geográficas comunes entre viajes y reservas,
    incorporando el factor antigüedad para definir el costo final de asignación.

    Esta función utiliza dos matrices calculadas mediante la función 'matriz_distancias_haversine':
      - Una matriz de distancias "puras" (distancia en línea recta entre el repartidor y el origen del envío).
      - Una matriz de coeficientes que es el resultado de dividir la distancia por la antigüedad del envío.
      
    Se aplican validaciones y penalizaciones sobre la matriz de coeficientes utilizando la distancia real,
    de forma que:
      - Si la distancia real supera el límite permitido (según el tipo de vehículo), se penaliza la asignación.
      - Para vehículos de tipo 4, si el valor de 'viaje["distancia"]' excede 'dist_max_entrega_v4', se penaliza.
    
    Los valores penalizados se asignan con un costo muy alto (999999999) para que no se escojan en la asignación.
    Para las métricas se utiliza la distancia real (pura) de cada asignación.

    Parámetros:
      - viajes (list): Lista de diccionarios con la información de los envíos.
      - reservas (list): Lista de diccionarios con la información de los repartidores.
      - dist_max_v1 (float): Distancia máxima permitida para asignar un envío a un repartidor con idVehiculo == 1.
      - dist_max_v4 (float): Distancia máxima permitida para asignar un envío a un repartidor con idVehiculo == 4.
      - dist_max_entrega_v4 (float): Distancia máxima de entrega permitida para repartidores con idVehiculo == 4.
      - tiempo_actual (datetime): Fecha y hora actuales para calcular la antigüedad de cada envío.

    Retorna:
      dict: Un diccionario que contiene:
            - "asignaciones": Lista de asignaciones realizadas, cada una con los datos del envío, la reserva y las distancias.
            - "distancia_total_metros": Suma total de las distancias reales (puras) de todas las asignaciones.
            - "distancia_promedio_idvehiculo_1": Promedio de distancias para asignaciones realizadas a vehículos de tipo 1.
            - "distancia_promedio_idvehiculo_4": Promedio de distancias para asignaciones realizadas a vehículos de tipo 4.
            - "metricas_por_direccion": Métricas detalladas agrupadas por cada dirección (idDireccion).
    """
    # Inicializar el resultado final y estructuras para las métricas
    resultado_final = {
        "asignaciones": [],
        "distancia_total_metros": 0,
        "distancia_promedio_idvehiculo_1": 0,
        "distancia_promedio_idvehiculo_4": 0,
        "metricas_por_direccion": {}
    }
    metricas_por_dir = defaultdict(lambda: {
        "distancia_total": 0,
        "suma_1": 0,
        "count_1": 0,
        "suma_4": 0,
        "count_4": 0
    })

    # Agrupar viajes y reservas por idDireccion
    grupos_viajes = defaultdict(list)
    for viaje in viajes:
        grupos_viajes[viaje['idDireccion']].append(viaje)

    grupos_reservas = defaultdict(list)
    for reserva in reservas:
        grupos_reservas[reserva['idDireccion']].append(reserva)

    # Procesar cada dirección que se encuentre en ambos grupos
    direcciones_comunes = set(grupos_viajes.keys()) & set(grupos_reservas.keys())
    for id_dir in direcciones_comunes:
        sub_viajes = grupos_viajes[id_dir]
        sub_reservas = grupos_reservas[id_dir]

        # Obtener ambas matrices:
        #   - 'distancias_puras': contiene la distancia real (en metros) entre cada par (reserva, envío).
        #   - 'matriz_coeficientes': es la matriz de costo que incorpora el factor antigüedad.
        # Se asume que la función 'matriz_distancias_haversine' tiene el siguiente prototipo:
        #     def matriz_distancias_haversine(repas, envios, tiempo_actual, return_both=False):
        #         ...
        #         if return_both:
        #             return distancias_puras, coeficientes
        #         else:
        #             return coeficientes
        distancias_puras, matriz_coeficientes = matriz_distancias_haversine(
            sub_reservas, sub_viajes, tiempo_actual, return_both=True
        )

        # Aplicar validaciones y controles utilizando la distancia real
        for i, reserva in enumerate(sub_reservas):
            vehiculo = reserva['idVehiculo']
            for j, viaje in enumerate(sub_viajes):
                distancia_real = distancias_puras[i, j]

                # Determinar la distancia máxima permitida según el tipo de vehículo
                if vehiculo == 1:
                    distancia_maxima = dist_max_v1
                elif vehiculo == 4:
                    distancia_maxima = dist_max_v4
                else:
                    distancia_maxima = 999999999  # Valor muy alto para otros tipos de vehículos

                # Si la distancia real excede la permitida, se penaliza la celda en la matriz de coeficientes.
                if distancia_real > distancia_maxima:
                    matriz_coeficientes[i, j] = 999999999

                # Regla adicional: para vehículos de tipo 4, si el envío tiene una 'distancia' mayor a 'dist_max_entrega_v4',
                # se penaliza la asignación.
                if vehiculo == 4 and viaje.get('distancia', 0) > dist_max_entrega_v4:
                    matriz_coeficientes[i, j] = 999999999

        # Resolver el problema de asignación utilizando el algoritmo húngaro sobre la matriz de coeficientes final
        filas_ind, columnas_ind = linear_sum_assignment(matriz_coeficientes)

        # Procesar las asignaciones válidas
        for idx in range(len(filas_ind)):
            i = filas_ind[idx]
            j = columnas_ind[idx]
            costo_asignacion = matriz_coeficientes[i, j]
            # Si el costo es penalizado, se ignora la asignación
            if costo_asignacion >= 999999999:
                continue

            reserva_asignada = sub_reservas[i]
            viaje_asignado = sub_viajes[j]
            # Se utiliza la distancia real para las métricas y detalles de la asignación
            distancia_real = distancias_puras[i, j]

            # Acumular la distancia total
            resultado_final["distancia_total_metros"] += distancia_real

            # Acumular métricas según el tipo de vehículo
            if reserva_asignada['idVehiculo'] == 1:
                metricas_por_dir[id_dir]["suma_1"] += distancia_real
                metricas_por_dir[id_dir]["count_1"] += 1
            elif reserva_asignada['idVehiculo'] == 4:
                metricas_por_dir[id_dir]["suma_4"] += distancia_real
                metricas_por_dir[id_dir]["count_4"] += 1

            metricas_por_dir[id_dir]["distancia_total"] += distancia_real

            # Registrar la asignación en el formato solicitado
            asignacion_registro = {
                "$id": f"{id_dir}-{len(resultado_final['asignaciones'])+1}",
                "IdViaje": viaje_asignado['id'],
                "IdReserva": reserva_asignada['id'],
                "DistanciaPickeo": round(distancia_real, 2),
                "Coeficiente": round(costo_asignacion, 2)
            }
            resultado_final["asignaciones"].append(asignacion_registro)

    # Calcular promedios globales para cada tipo de vehículo
    total_distancia_v1 = 0
    total_distancia_v4 = 0
    total_count_v1 = 0
    total_count_v4 = 0

    for id_dir, metrics in metricas_por_dir.items():
        total_distancia_v1 += metrics["suma_1"]
        total_count_v1 += metrics["count_1"]
        total_distancia_v4 += metrics["suma_4"]
        total_count_v4 += metrics["count_4"]

    if total_count_v1 > 0:
        resultado_final["distancia_promedio_idvehiculo_1"] = round(total_distancia_v1 / total_count_v1, 2)
    if total_count_v4 > 0:
        resultado_final["distancia_promedio_idvehiculo_4"] = round(total_distancia_v4 / total_count_v4, 2)

    resultado_final["distancia_total_metros"] = round(resultado_final["distancia_total_metros"], 2)

    # Calcular y almacenar las métricas por cada dirección
    for id_dir, metrics in metricas_por_dir.items():
        if metrics["count_1"] > 0:
            promedio_v1 = round(metrics["suma_1"] / metrics["count_1"], 2)
        else:
            promedio_v1 = 0
        if metrics["count_4"] > 0:
            promedio_v4 = round(metrics["suma_4"] / metrics["count_4"], 2)
        else:
            promedio_v4 = 0

        resultado_final["metricas_por_direccion"][id_dir] = {
            "distancia_total_metros": round(metrics["distancia_total"], 2),
            "distancia_promedio_idvehiculo_1": promedio_v1,
            "distancia_promedio_idvehiculo_4": promedio_v4
        }

    return resultado_final


from collections import defaultdict
from scipy.optimize import linear_sum_assignment
import numpy as np
# Se asume que la función matriz_distancias_haversine está definida/importada desde algún módulo (por ejemplo, Utils)

from collections import defaultdict
from scipy.optimize import linear_sum_assignment
# Se asume que la función matriz_distancias_haversine está definida/importada desde algún módulo (por ejemplo, Utils)

def asignar_repas_envios_zonas_migrantes(
    viajes,
    reservas,
    dist_max_v1,
    dist_max_v4,
    dist_max_entrega_v4,
    tiempo_actual,
    usar_limite_pickeo_migrante=True,
    usar_limite_entrega_migrante=True
):
    """
    Asigna repartidores a envíos por zonas considerando primero los envíos migrantes y luego
    aplicando la asignación normal a lo que quede.

    Parámetros:
      - viajes (list): Lista de diccionarios con la información de los envíos. Se espera que cada
                       viaje tenga 'id', 'idDireccion' (origen) y 'idDireccion_destino' (destino).
      - reservas (list): Lista de diccionarios con la información de los repartidores. Se espera que cada
                         reserva tenga 'id', 'idDireccion' (actual) e 'idDireccion_calculada' (localización original),
                         además de 'idVehiculo'.
      - dist_max_v1 (float): Distancia máxima permitida para asignar un envío a un repartidor con idVehiculo == 1.
      - dist_max_v4 (float): Distancia máxima permitida para asignar un envío a un repartidor con idVehiculo == 4.
      - dist_max_entrega_v4 (float): Distancia máxima de entrega permitida para repartidores con idVehiculo == 4.
      - tiempo_actual: Fecha y hora actual para el cálculo de antigüedad en la función matriz_distancias_haversine.
      - usar_limite_pickeo_migrante (bool): Si es True, se aplican los límites de distancia de pickeo en el bloque migrante.
      - usar_limite_entrega_migrante (bool): Si es True, se aplica el límite de distancia de entrega para vehículos (idVehiculo == 4)
                                              en el bloque migrante.

    Retorna:
      dict: Con las siguientes claves:
            - "asignaciones": Lista de asignaciones realizadas (cada una con un campo "migrante": True/False).
            - "distancia_total_metros": Suma total de las distancias reales de todas las asignaciones.
            - "distancia_promedio_idvehiculo_1": Promedio de distancias para asignaciones a vehículos tipo 1.
            - "distancia_promedio_idvehiculo_4": Promedio de distancias para asignaciones a vehículos tipo 4.
            - "metricas_por_direccion": Métricas agrupadas por zona (usando el origen, idDireccion).
    """
    # Inicialización del resultado final y estructuras de control
    result_final = {
        "asignaciones": [],
        "distancia_total_metros": 0,
        "distancia_promedio_idvehiculo_1": 0,
        "distancia_promedio_idvehiculo_4": 0,
        "metricas_por_direccion": {}
    }
    # Para evitar que un viaje o reserva se asigne en ambos bloques
    assigned_viaje_ids = set()
    assigned_reserva_ids = set()

    # BLOQUE MIGRANTE: asignación de envíos migrantes
    # Un envío migrante: viaje['idDireccion'] != viaje['idDireccion_destino']
    migrant_viajes = [v for v in viajes if v['idDireccion'] != v['idDireccion_destino']]
    # Un repartidor en migración: reserva['idDireccion'] != reserva['idDireccion_calculada']
    migrant_reservas = [r for r in reservas if r['idDireccion'] != r['idDireccion_calculada']]

    # Agrupar los viajes migrantes por par (origen, destino) = (Z, W)
    grupos_migrantes_viajes = defaultdict(list)
    for viaje in migrant_viajes:
        key = (viaje['idDireccion'], viaje['idDireccion_destino'])
        grupos_migrantes_viajes[key].append(viaje)

    # Agrupar las reservas migrantes según: (idDireccion_calculada, idDireccion)
    # Esto corresponde a (zona original, zona actual) y debe coincidir con (Z, W) del viaje.
    grupos_migrantes_reservas = defaultdict(list)
    for reserva in migrant_reservas:
        key = (reserva['idDireccion_calculada'], reserva['idDireccion'])
        grupos_migrantes_reservas[key].append(reserva)

    # Para cada par (Z, W) que esté en ambos grupos, intentar asignar
    keys_migrantes = set(grupos_migrantes_viajes.keys()) & set(grupos_migrantes_reservas.keys())
    for key in keys_migrantes:
        sub_viajes = grupos_migrantes_viajes[key]
        sub_reservas = grupos_migrantes_reservas[key]
        # Obtener matrices: distancias reales y matriz de coeficientes para asignación
        dist_puras, matriz_coef = matriz_distancias_haversine(sub_reservas, sub_viajes, tiempo_actual, return_both=True)
        # Aplicar validaciones según los máximos permitidos
        for i, reserva in enumerate(sub_reservas):
            vehiculo = reserva['idVehiculo']
            for j, viaje in enumerate(sub_viajes):
                distancia_real = dist_puras[i, j]
                # Aplicar límite de pickeo solo si se indica
                if usar_limite_pickeo_migrante:
                    if vehiculo == 1:
                        distancia_maxima = dist_max_v1
                    elif vehiculo == 4:
                        distancia_maxima = dist_max_v4
                    else:
                        distancia_maxima = 999999999
                    if distancia_real > distancia_maxima:
                        matriz_coef[i, j] = 999999999
                # Aplicar límite de entrega para vehículos tipo 4 solo si se indica
                if usar_limite_entrega_migrante and vehiculo == 4 and viaje.get('distancia', 0) > dist_max_entrega_v4:
                    matriz_coef[i, j] = 999999999

        # Resolver el problema de asignación (algoritmo húngaro)
        filas_ind, columnas_ind = linear_sum_assignment(matriz_coef)
        for idx in range(len(filas_ind)):
            i = filas_ind[idx]
            j = columnas_ind[idx]
            costo_asignacion = matriz_coef[i, j]
            if costo_asignacion >= 999999999:
                continue
            reserva_asignada = sub_reservas[i]
            viaje_asignado = sub_viajes[j]
            distancia_real = dist_puras[i, j]
            asignacion_registro = {
                "$id": f"{key[0]}-{key[1]}-{len(result_final['asignaciones'])+1}",
                "IdViaje": viaje_asignado['id'],
                "IdReserva": reserva_asignada['id'],
                "DistanciaPickeo": round(distancia_real, 2),
                "Coeficiente": round(costo_asignacion, 2),
                "migrante": True
            }
            result_final["asignaciones"].append(asignacion_registro)
            result_final["distancia_total_metros"] += distancia_real
            # Actualizar métricas agrupadas por el origen (Z)
            if key[0] not in result_final["metricas_por_direccion"]:
                result_final["metricas_por_direccion"][key[0]] = {"distancia_total_metros": 0, "suma_1": 0, "count_1": 0, "suma_4": 0, "count_4": 0}
            result_final["metricas_por_direccion"][key[0]]["distancia_total_metros"] += distancia_real
            if reserva_asignada['idVehiculo'] == 1:
                result_final["metricas_por_direccion"][key[0]]["suma_1"] += distancia_real
                result_final["metricas_por_direccion"][key[0]]["count_1"] += 1
            elif reserva_asignada['idVehiculo'] == 4:
                result_final["metricas_por_direccion"][key[0]]["suma_4"] += distancia_real
                result_final["metricas_por_direccion"][key[0]]["count_4"] += 1

            assigned_viaje_ids.add(viaje_asignado['id'])
            assigned_reserva_ids.add(reserva_asignada['id'])

    # FIN BLOQUE MIGRANTE

    # BLOQUE NORMAL: asignación de los envíos que quedan (tanto no migrantes como migrantes sin asignar)
    remaining_viajes = [v for v in viajes if v['id'] not in assigned_viaje_ids]
    remaining_reservas = [r for r in reservas if r['id'] not in assigned_reserva_ids]

    # Agrupar por zona (usando el origen, 'idDireccion')
    grupos_viajes = defaultdict(list)
    for viaje in remaining_viajes:
        grupos_viajes[viaje['idDireccion']].append(viaje)
    grupos_reservas = defaultdict(list)
    for reserva in remaining_reservas:
        grupos_reservas[reserva['idDireccion']].append(reserva)

    zonas_comunes = set(grupos_viajes.keys()) & set(grupos_reservas.keys())
    for id_dir in zonas_comunes:
        sub_viajes = grupos_viajes[id_dir]
        sub_reservas = grupos_reservas[id_dir]
        dist_puras, matriz_coef = matriz_distancias_haversine(sub_reservas, sub_viajes, tiempo_actual, return_both=True)
        for i, reserva in enumerate(sub_reservas):
            vehiculo = reserva['idVehiculo']
            for j, viaje in enumerate(sub_viajes):
                distancia_real = dist_puras[i, j]
                if vehiculo == 1:
                    distancia_maxima = dist_max_v1
                elif vehiculo == 4:
                    distancia_maxima = dist_max_v4
                else:
                    distancia_maxima = 999999999
                if distancia_real > distancia_maxima:
                    matriz_coef[i, j] = 999999999
                if vehiculo == 4 and viaje.get('distancia', 0) > dist_max_entrega_v4:
                    matriz_coef[i, j] = 999999999
        filas_ind, columnas_ind = linear_sum_assignment(matriz_coef)
        for idx in range(len(filas_ind)):
            i = filas_ind[idx]
            j = columnas_ind[idx]
            costo_asignacion = matriz_coef[i, j]
            if costo_asignacion >= 999999999:
                continue
            reserva_asignada = sub_reservas[i]
            viaje_asignado = sub_viajes[j]
            distancia_real = dist_puras[i, j]
            asignacion_registro = {
                "$id": f"{id_dir}-{len(result_final['asignaciones'])+1}",
                "IdViaje": viaje_asignado['id'],
                "IdReserva": reserva_asignada['id'],
                "DistanciaPickeo": round(distancia_real, 2),
                "Coeficiente": round(costo_asignacion, 2),
                "migrante": False
            }
            result_final["asignaciones"].append(asignacion_registro)
            result_final["distancia_total_metros"] += distancia_real
            if id_dir not in result_final["metricas_por_direccion"]:
                result_final["metricas_por_direccion"][id_dir] = {"distancia_total_metros": 0, "suma_1": 0, "count_1": 0, "suma_4": 0, "count_4": 0}
            result_final["metricas_por_direccion"][id_dir]["distancia_total_metros"] += distancia_real
            if reserva_asignada['idVehiculo'] == 1:
                result_final["metricas_por_direccion"][id_dir]["suma_1"] += distancia_real
                result_final["metricas_por_direccion"][id_dir]["count_1"] += 1
            elif reserva_asignada['idVehiculo'] == 4:
                result_final["metricas_por_direccion"][id_dir]["suma_4"] += distancia_real
                result_final["metricas_por_direccion"][id_dir]["count_4"] += 1

    # Calcular promedios globales para cada tipo de vehículo
    total_dist_v1 = 0
    count_v1 = 0
    total_dist_v4 = 0
    count_v4 = 0
    for metrics in result_final["metricas_por_direccion"].values():
        total_dist_v1 += metrics["suma_1"]
        count_v1 += metrics["count_1"]
        total_dist_v4 += metrics["suma_4"]
        count_v4 += metrics["count_4"]
    if count_v1 > 0:
        result_final["distancia_promedio_idvehiculo_1"] = round(total_dist_v1 / count_v1, 2)
    if count_v4 > 0:
        result_final["distancia_promedio_idvehiculo_4"] = round(total_dist_v4 / count_v4, 2)
    result_final["distancia_total_metros"] = round(result_final["distancia_total_metros"], 2)

    return result_final