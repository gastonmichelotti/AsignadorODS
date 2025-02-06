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

Body de la petición:

- viajes: Lista de objetos JSON que describen los viajes.
- reservas: Lista de objetos JSON que describen los repartidores (reservas).

Ejemplo:
```json 
{
  "viajes": [
    {
      "distancia": 3115.0,
      "id": 12942149,
      "idUsuario": 16556,
      "idDireccion": 30635,
      "idDireccion_destino": 30635,
      "latitudOrigen": -34.608138, 
      "longitudOrigen": -58.37507,
      "fechaProcesamiento": "2024-01-15T14:20:00"
    },
    {
      "distancia": 1625.0,
      "id": 12942151,
      "idUsuario": 16556,
      "idDireccion": 30635,
      "idDireccion_destino": 30635,
      "latitudOrigen": -34.623582, 
      "longitudOrigen": -58.399646,
      "fechaProcesamiento": "2024-01-15T14:29:00"
    }    
  ],
  "reservas": [
    {
      "id": 6171164,
      "idDireccion": 30635,
      "idDireccion_calculada": 30635,
      "radioMaximoAsignacion": 8000,
      "latitud": -34.61175, 
      "longitud": -58.38278,
      "idUsuario": 23317,
      "idVehiculo": 4
    },
    {
      "id": 6171165,
      "idDireccion": 30635,
      "idDireccion_calculada": 30635,
      "radioMaximoAsignacion": 8000,
      "latitud": -34.61175, 
      "longitud": -58.38278,
      "idUsuario": 23317,
      "idVehiculo": 1
    }   
  ],
  "DistanciaMaximaVehiculo1": 8000,
  "DistanciaMaximaVehiculo4": 3000,
  "DistanciaMaximaEntregaVehiculo4": 3000,
  "CurrentTime": "2024-01-15T14:30:00"
}
```

Respuesta (ejemplo):
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

Body de la petición:
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
- **DistanciaMaximaEntregaVehiculo4**: Distancia máxima en metros que tiene que tener un viaje de origen a destino para que se asigne a un repartidor con **idVehiculo = 4**.

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

Respuesta (ejemplo):
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

**Campos de la respuesta:**
- **asignaciones**: Lista de objetos que vinculan un viaje con una reserva.
- **$id**: En este ejemplo, concatena `idDireccion` con la posición de la asignación (por ejemplo, "1-1", "2-2", etc.).
- **distancia_total_metros**: Suma total de las distancias de todas las asignaciones.
- **distancia_promedio_idvehiculo_1** y **distancia_promedio_idvehiculo_4**: Promedio de distancias según el tipo de vehículo (1 o 4) a nivel global.
- **metricas_por_direccion**:
  - **distancia_total_metros**: Suma de distancias en dicha dirección.
  - **distancia_promedio_idvehiculo_1** y **distancia_promedio_idvehiculo_4**: Promedios de distancias para cada tipo de vehículo dentro de esa dirección específica.

**Validaciones de Distancia Máxima**
En este endpoint, si la distancia calculada entre una reserva y un viaje excede la distancia máxima permitida para el `idVehiculo` de esa reserva, esa combinación no se asignará (se penaliza para que el algoritmo la descarte).

**Consideraciones Adicionales**
- Asegúrate de que **DistanciaMaximaVehiculo1** y **DistanciaMaximaVehiculo4** sean valores numéricos (float/int).
- Si un repartidor tiene un `idVehiculo` distinto de 1 o 4, el comportamiento puede variar según la implementación (por ejemplo, sin restricción o con un valor “infinito” por defecto).
- Puedes usar herramientas como **Postman** o **cURL** para probar los endpoints.

#### *3. POST /asignar_repas_zonas_migrantes*

Asigna repartidores a viajes considerando zonas con reglas especiales para migrantes. Este endpoint extiende la lógica del endpoint de zonas incorporando un parámetro adicional que indica si el viaje o la reserva corresponde a un migrante.

Body de la petición:
- **viajes**: Lista de objetos JSON que describen los viajes, con:
  - **id**
  - **idDireccion**
  - **latitudOrigen**
  - **longitudOrigen**
  - **esMigrante** (booleano) – Indica si el viaje corresponde a un migrante.
  - *(otros campos requeridos)*
  
- **reservas**: Lista de objetos JSON que describen los repartidores (reservas), con:
  - **id**
  - **idVehiculo**
  - **idDireccion**
  - **latitud**
  - **longitud**
  - **esMigrante** (booleano) – Indica si el repartidor es migrante.
  - *(otros campos requeridos)*
  
- **DistanciaMaximaVehiculo1**: Distancia máxima en metros para asignar viajes a un repartidor con **idVehiculo = 1**.
- **DistanciaMaximaVehiculo4**: Distancia máxima en metros para asignar viajes a un repartidor con **idVehiculo = 4**.
- **DistanciaMaximaEntregaVehiculo4**: Distancia máxima en metros que debe cumplir el viaje de origen a destino para que se asigne a un repartidor con **idVehiculo = 4**.

Ejemplo de body:
```json
{
  "viajes": [
    {
      "distancia": 1070.0,
      "id": 1111, 
      "idUsuario": 16556,
      "idDireccion": 2820679,
      "idDireccion_destino": 2820679,
      "latitudOrigen": -34.62622, 
      "longitudOrigen": -58.42298, 
      "fechaProcesamiento": "2024-01-15T14:29:00"
    },
    {
      "distancia": 2010.0,
      "id": 2222, 
      "idUsuario": 16556,
      "idDireccion": 2820679,
      "idDireccion_destino": 2820688,
      "latitudOrigen": -34.63046, 
      "longitudOrigen": -58.41886,
      "fechaProcesamiento": "2024-01-15T14:29:00"
    },
    {
      "distancia": 1650.0,
      "id": 3333,
      "idUsuario": 16556,
      "idDireccion": 2820679,
      "idDireccion_destino": 2820667,
      "latitudOrigen": -34.6244, 
      "longitudOrigen": -58.43527,
      "fechaProcesamiento": "2024-01-15T14:29:00"
    }        
  ],
  "reservas": [
    {
      "id": 9999,
      "idDireccion": 2820679,
      "idDireccion_calculada": 2820679,
      "radioMaximoAsignacion": 8000,
      "latitud": -34.627,  
      "longitud": -58.42677,
      "idUsuario": 23317,
      "idVehiculo": 4
    },
     {
      "id": 8888, 
      "idDireccion": 2820688,
      "idDireccion_calculada": 2820679,
      "radioMaximoAsignacion": 8000,
      "latitud": -34.627,  
      "longitud": -58.42677,
      "idUsuario": 23317,
      "idVehiculo": 1
    },
     {
      "id": 7777, 
      "idDireccion": 2820667,
      "idDireccion_calculada": 2820679,
      "radioMaximoAsignacion": 8000,
      "latitud": -34.627,  
      "longitud": -58.42677,
      "idUsuario": 23317,
      "idVehiculo": 4
    },
     {
      "id": 6666, 
      "idDireccion": 2820663,
      "idDireccion_calculada": 2820679,
      "radioMaximoAsignacion": 8000,
      "latitud": -34.627,  
      "longitud": -58.42677,
      "idUsuario": 23317,
      "idVehiculo": 1
    }
  ],
  "DistanciaMaximaVehiculo1": 8000,
  "DistanciaMaximaVehiculo4": 3000,
  "DistanciaMaximaEntregaVehiculo4": 3000,
  "CurrentTime": "2024-01-15T14:30:00"
}

```

Respuesta (ejemplo):
```json
{
  "asignaciones": [
    {
      "$id": "10-1",
      "IdViaje": 201,
      "IdReserva": 301,
      "DistanciaPickeo": 70.5,
      "Coeficiente": 70.5
    },
    {
      "$id": "11-2",
      "IdViaje": 202,
      "IdReserva": 302,
      "DistanciaPickeo": 60.2,
      "Coeficiente": 60.2
    }
  ],
  "distancia_total_metros": 130.7,
  "distancia_promedio_idvehiculo_1": 70.5,
  "distancia_promedio_idvehiculo_4": 60.2,
  "metricas_por_direccion": {
    "10": {
      "distancia_total_metros": 70.5,
      "distancia_promedio_idvehiculo_1": 70.5,
      "distancia_promedio_idvehiculo_4": 0
    },
    "11": {
      "distancia_total_metros": 60.2,
      "distancia_promedio_idvehiculo_1": 0,
      "distancia_promedio_idvehiculo_4": 60.2,
      "CurrentTime": "2024-01-15T14:30:00"
    }
  }
}
```

**Campos de la respuesta:**
- **asignaciones**: Lista de objetos que vinculan un viaje con una reserva.
- **$id**: En este ejemplo, concatena `idDireccion` con la posición de la asignación (por ejemplo, "10-1", "11-2", etc.).
- **distancia_total_metros**: Suma total de las distancias de todas las asignaciones.
- **distancia_promedio_idvehiculo_1** y **distancia_promedio_idvehiculo_4**: Promedio de distancias según el tipo de vehículo a nivel global.
- **metricas_por_direccion**:
  - **distancia_total_metros**: Suma de distancias en la dirección correspondiente.
  - **distancia_promedio_idvehiculo_1** y **distancia_promedio_idvehiculo_4**: Promedios de distancias para cada tipo de vehículo dentro de la dirección.

**Validaciones de Distancia Máxima**
Al igual que en los endpoints anteriores, si la distancia calculada entre una reserva y un viaje excede la distancia máxima permitida para el `idVehiculo` de la reserva, la asignación será descartada.

**Consideraciones Adicionales**
- Asegúrate de que **DistanciaMaximaVehiculo1** y **DistanciaMaximaVehiculo4** sean valores numéricos (float/int).
- Si un repartidor tiene un `idVehiculo` distinto de 1 o 4, el comportamiento puede variar según la implementación (por ejemplo, sin restricción o con un valor “infinito” por defecto).
- Puedes usar herramientas como **Postman** o **cURL** para probar el endpoint.

¡Listo! Con estos cambios, la funcionalidad de distancia máxima de asignación y la forma de consumir los endpoints quedan debidamente documentadas, incluyendo el nuevo endpoint para asignaciones en zonas migrantes.