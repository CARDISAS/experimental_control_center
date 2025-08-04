# Cardi Control – Experimental Control Center

Repositorio refactorizado (agosto 2025) conforme a la nueva arquitectura modular.

## Piezas principales

* **Firmware** – ESP32 expone Modbus‑TCP (puerto 502)
* **Collector** – micro‑servicio Python que sondea registros Modbus y persiste en TimescaleDB
* **Command API** – FastAPI REST + WebSocket, escribe Coils (válvulas) y entrega datos en tiempo real
* **Scheduler** – reglas de riego externas al MCU (opcional)
* **MQTT Bridge** – publica lecturas a topics (opcional)
* **UI** – dashboard React (placeholder)

Para arrancar todo:

```bash
docker compose up -d --build
```

Documentación detallada en `docs/`.
