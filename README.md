## Asignador de Repartidores

Este proyecto utiliza Flask para exponer endpoints que asignan repartidores a viajes bajo distintas lógicas:

1. **Asignación simple** (sin considerar zonas), basado en la minimización de distancia.
2. **Asignación por zonas** (considera la misma dirección de reparto para agrupar y asignar), con posibilidad de restringir la distancia máxima en función del tipo de vehículo.

### Requerimientos

- Python 3.7+
- Flask
- Numpy
- SciPy
- (Opcional) Cualquier otra librería mencionada en tus ficheros.

```bash pip install -r requirements.txt```

### Ejecutar el proyecto

Para correr la aplicación localmente:

```bash python app.py```

Esto levantará un servidor en el puerto 5005 (por defecto).

### Endpoints

#### *1. POST /asignar_repas*

Asigna repartidores a viajes sin considerar zonas diferenciadas.
La asignación se realiza basándose en la distancia geográfica mínima (calculo Haversine + algoritmo húngaro).

Body de la petición

- viajes: Lista de objetos JSON que describen los viajes.
- reservas: Lista de objetos JSON que describen los repartidores (reservas).

Ejemplo:
```json 
{
  "viajes": [
    {
      "id": 101,
      "latitudOrigen": -34.603722,
      "longitudOrigen": -58.381592
      // otros campos...
    },
    {
      "id": 102,
      "latitudOrigen": -34.600000,
      "longitudOrigen": -58.370000
      // otros campos...
    }
  ],
  "reservas": [
    {
      "id": 201,
      "idVehiculo": 1,
      "latitud": -34.603000,
      "longitud": -58.381000
      // otros campos...
    },
    {
      "id": 202,
      "idVehiculo": 4,
      "latitud": -34.601000,
      "longitud": -58.370500
      // otros campos...
    }
  ]
}
```

Respuesta (ejemplo)
```json
{
  "asignaciones": [
    {
      "$id": "1",
      "IdViaje": 101,
      "IdReserva": 201,
      "DistanciaPickeo": 68.61,
      "Coeficiente": 68.61
    },
    {
      "$id": "2",
      "IdViaje": 102,
      "IdReserva": 202,
      "DistanciaPickeo": 35.42,
      "Coeficiente": 35.42
    }
  ],
  "distancia_total_metros": 104.03,
  "distancia_promedio_idvehiculo_1": 68.61,
  "distancia_promedio_idvehiculo_4": 35.42
}
```

**Campos de la respuesta:**
- **asignaciones**: Lista de objetos que vinculan un viaje con una reserva, incluyendo la distancia calculada.
- **distancia_total_metros**: Suma total de las distancias de pickeo.
- **distancia_promedio_idvehiculo_1**: Promedio de las distancias para vehículos con idVehiculo = 1.
- **distancia_promedio_idvehiculo_4**: Promedio de las distancias para vehículos con idVehiculo = 4.

#### *2. POST /asignar_repas_zonas*

Asigna repartidores a viajes considerando zonas (direcciones) y restricciones de distancia máxima.

Cada viaje y cada reserva tienen un campo idDireccion que se utiliza para agruparlos en la misma “zona” antes de asignar.
Además, aquí se permite establecer la distancia máxima permitida (en metros) para cada tipo de vehículo.

Body de la petición
- **viajes**: Lista de objetos JSON que describen los viajes, con:
  - **id**
  - **idDireccion**
  - **latitudOrigen**
  - **longitudOrigen**
  - *(otros campos requeridos)*
  
- **reservas**: Lista de objetos JSON que describen los repartidores (reservas), con:
  - **id**
  - **idVehiculo**
  - **idDireccion**
  - **latitud**
  - **longitud**
  - *(otros campos requeridos)*
  
- **DistanciaMaximaVehiculo1**: Distancia máxima en metros para asignar viajes a un repartidor con **idVehiculo = 1**.
- **DistanciaMaximaVehiculo4**: Distancia máxima en metros para asignar viajes a un repartidor con **idVehiculo = 4**.
- **DistanciaMaximaEntregaVehiculo4**: Distancia máxima en metros que tiene que tener un viaje de origen a desitno para que se asigne a un repartidor con **idVehiculo = 4**.

Ejemplo de body:
```json
{
  "viajes": [
    {
      "id": 101,
      "idDireccion": 1,
      "latitudOrigen": -34.603722,
      "longitudOrigen": -58.381592
    },
    {
      "id": 102,
      "idDireccion": 2,
      "latitudOrigen": -34.600000,
      "longitudOrigen": -58.370000
    }
  ],
  "reservas": [
    {
      "id": 201,
      "idVehiculo": 1,
      "idDireccion": 1,
      "latitud": -34.603000,
      "longitud": -58.381000
    },
    {
      "id": 202,
      "idVehiculo": 4,
      "idDireccion": 2,
      "latitud": -34.601000,
      "longitud": -58.370500
    }
  ],
  "DistanciaMaximaVehiculo1": 3000,
  "DistanciaMaximaVehiculo4": 5000,
  "DistanciaMaximaEntregaVehiculo4": 3000
}
```
Respuesta (ejemplo)
```json
{
  "asignaciones": [
    {
      "$id": "1-1",
      "IdViaje": 101,
      "IdReserva": 201,
      "DistanciaPickeo": 68.61,
      "Coeficiente": 68.61
    },
    {
      "$id": "2-2",
      "IdViaje": 102,
      "IdReserva": 202,
      "DistanciaPickeo": 55.3,
      "Coeficiente": 55.3
    }
  ],
  "distancia_total_metros": 123.91,
  "distancia_promedio_idvehiculo_1": 68.61,
  "distancia_promedio_idvehiculo_4": 55.3,
  "metricas_por_direccion": {
    "1": {
      "distancia_total_metros": 68.61,
      "distancia_promedio_idvehiculo_1": 68.61,
      "distancia_promedio_idvehiculo_4": 0
    },
    "2": {
      "distancia_total_metros": 55.3,
      "distancia_promedio_idvehiculo_1": 0,
      "distancia_promedio_idvehiculo_4": 55.3,
      "CurrentTime": "2024-01-15T14:30:00"
    }
  }
}
```
## Campos de la respuesta
- **asignaciones**: Lista de objetos que vinculan un viaje con una reserva.
- **$id**: En este ejemplo, concatena `idDireccion` con la posición de la asignación (por ejemplo, "1-1", "2-2", etc.).
- **distancia_total_metros**: Suma total de las distancias de todas las asignaciones.
- **distancia_promedio_idvehiculo_1** y **distancia_promedio_idvehiculo_4**: Promedio de distancias según el tipo de vehículo (1 o 4) a nivel global.
- **metricas_por_direccion**:
  - **distancia_total_metros**: Suma de distancias en dicha dirección.
  - **distancia_promedio_idvehiculo_1** y **distancia_promedio_idvehiculo_4**: Promedios de distancias para cada tipo de vehículo dentro de esa dirección específica.

## Validaciones de Distancia Máxima
En este endpoint, si la distancia calculada entre una reserva y un viaje excede la distancia máxima permitida para el `idVehiculo` de esa reserva, esa combinación no se asignará (se penaliza para que el algoritmo la descarte).

## Consideraciones Adicionales
- Asegúrate de que **DistanciaMaximaVehiculo1** y **DistanciaMaximaVehiculo4** sean valores numéricos (float/int).
- Si un repartidor tiene un `idVehiculo` distinto de 1 o 4, el comportamiento puede variar según la implementación (por ejemplo, sin restricción o con un valor “infinito” por defecto).
- Puedes usar herramientas como **Postman** o **cURL** para probar los endpoints.

¡Listo! Con estos cambios, la funcionalidad de distancia máxima de asignación y la forma de consumir los endpoints quedan debidamente documentadas.