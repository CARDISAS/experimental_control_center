## Arquitectura lógica

```mermaid
graph LR
    subgraph Field
        MCU[ESP32 Modbus-TCP]
    end
    subgraph Backend
        COL[Collector]
        API[Command API]
        REDIS[Redis Cache]
        DB[(TimescaleDB)]
    end
    MCU -->|Modbus 502| COL
    COL --> DB
    COL --> REDIS
    API -->|read/write| REDIS
    API -->|write_single_coil| MCU
```

* El Collector lee Holding Registers y Coils cada segundo.
* Command API expone `/api/*` y WebSocket; toma datos de Redis y escribe Coils.
* TimescaleDB guarda el histórico para Grafana.
