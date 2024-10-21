# AsignadorODS

Este proyecto implementa un sistema de asignación de repartidores a envíos utilizando clustering y optimización de distancias geográficas. Se utiliza un algoritmo húngaro para la asignación óptima, y la aplicación está desarrollada en Python con una API Flask.

## Funcionalidades

- **Asignación de Repartidores a Envíos:** 
  - El sistema genera asignaciones óptimas basadas en distancias geográficas calculadas con la fórmula de Haversine.
- **API Flask:** 
  - La API permite realizar las asignaciones a través de un EndPoint, devolviendo las asignaciones en formato JSON.
- **Soporte multiplataforma:** 
  - Inicia y detiene el proceso de la API en macOS y Windows con scripts de automatización.

## Requisitos

- Python 3.x instalado
- Git instalado para clonar el repositorio
- Virtualenv o venv para entornos virtuales

## WINDOWS

- Inicia la api haciendo click en el archivo 'iniciarAsignador.bat'
- Detiene la api haciendo click en el archivo 'detenerAsignador.bat'

## MACOS

- Inicia la api haciendo click en el archivo 'IniciarASignador.app'
- Detiene la api haciendo click en el archivo 'DetenerAsignador.app'

## ENDPOINT

URL:  http://localhost:5005/asignar_repas o http://127.0.0.1:5005/asignar_repas

METODO: POST

HEADERS:
- Content-Type: application/json

EJEMPLO DE BODY:
```json
{
  "viajes": [
    {
      "distancia": 1931.27,
      "id": 1,
      "idUsuario": 16556,
      "latitudOrigen": -34.58567,
      "longitudOrigen": -58.46624,
      "idDireccion": 30635
    },
    {
      "distancia": 838.94,
      "id": 2,
      "idUsuario": 16556,
      "latitudOrigen": -34.62064,
      "longitudOrigen": -58.46504,
      "idDireccion": 30635
    },
    {
      "distancia": 606.69,
      "id": 3,
      "idUsuario": 16556,
      "latitudOrigen": -34.61047,
      "longitudOrigen": -58.40599,
      "idDireccion": 30635
    },
    {
      "distancia": 1955.25,
      "id": 4,
      "idUsuario": 16556,
      "latitudOrigen": -34.58421,
      "longitudOrigen": -58.43667,
      "idDireccion": 30635
    },
    {
      "distancia": 984.95,
      "id": 5,
      "idUsuario": 16556,
      "latitudOrigen": -34.59268,
      "longitudOrigen": -58.45499,
      "idDireccion": 30635
    }
  ],
  "reservas": [
    {
      "idDireccion": 30635,
      "idUsuario": 23317,
      "id": 1,
      "latitud": -34.57875,
      "longitud": -58.4574,
      "idVehiculo": 4,
      "radioMaximoAsignacion": 3000
    },
    {
      "idDireccion": 30635,
      "idUsuario": 23317,
      "id": 2,
      "latitud": -34.61499,
      "longitud": -58.47551,
      "idVehiculo": 1,
      "radioMaximoAsignacion": 8000
    },
    {
      "idDireccion": 30635,
      "idUsuario": 23317,
      "id": 3,
      "latitud": -34.59987,
      "longitud": -58.41337,
      "idVehiculo": 4,
      "radioMaximoAsignacion": 3000
    },
    {
      "idDireccion": 30635,
      "idUsuario": 23317,
      "id": 4,
      "latitud": -34.5804,
      "longitud": -58.42911,
      "idVehiculo": 4,
      "radioMaximoAsignacion": 3000
    },
    {
      "idDireccion": 30635,
      "idUsuario": 23317,
      "id": 5,
      "latitud": -34.59781,
      "longitud": -58.46099,
      "idVehiculo": 1,
      "radioMaximoAsignacion": 8000
    }
  ]
}
```

EJEMPLO DE RESPUESTA:
``` json
{
    "asignaciones": [
        {
            "$id": "1",
            "Coeficiente": 1116.7,
            "DistanciaPickeo": 1116.7,
            "IdReserva": 1,
            "IdViaje": 1
        },
        {
            "$id": "2",
            "Coeficiente": 1145.71,
            "DistanciaPickeo": 1145.71,
            "IdReserva": 2,
            "IdViaje": 2
        },
        {
            "$id": "3",
            "Coeficiente": 1358.48,
            "DistanciaPickeo": 1358.48,
            "IdReserva": 3,
            "IdViaje": 3
        },
        {
            "$id": "4",
            "Coeficiente": 811.47,
            "DistanciaPickeo": 811.47,
            "IdReserva": 4,
            "IdViaje": 4
        },
        {
            "$id": "5",
            "Coeficiente": 791.84,
            "DistanciaPickeo": 791.84,
            "IdReserva": 5,
            "IdViaje": 5
        }
    ],
    "distancia_promedio_idvehiculo_1": 968.78,
    "distancia_promedio_idvehiculo_4": 1095.55,
    "distancia_total_metros": 5224.21
}
```