import asyncio, os, datetime as dt, json, logging
from pymodbus.client import AsyncModbusTcpClient
import asyncpg
import redis.asyncio as redis

logging.basicConfig(level=logging.INFO)

MCU_HOST   = os.getenv("MCU_HOST", "esp32.local")
MCU_PORT   = int(os.getenv("MCU_PORT", "502"))
POLL       = float(os.getenv("POLL_INTERVAL", "1.0"))
PG_DSN     = os.getenv("PG_DSN", "postgresql://postgres:postgres@db:5432/postgres")
REDIS_URL  = os.getenv("REDIS_URL", "redis://redis:6379/0")
FLOW_K     = float(os.getenv("FLOW_K", "0.25"))     # litros por pulso

async def main() -> None:
    r    = redis.from_url(REDIS_URL)
    pool = await asyncpg.create_pool(PG_DSN)

    async with AsyncModbusTcpClient(MCU_HOST, MCU_PORT) as client:
        while True:
            rr = await client.read_holding_registers(0, 4, unit=1)   # ← ahora 4 regs
            if rr.isError():
                logging.error("Modbus error %s", rr)
            else:
                lux, ph_raw, ec_raw, flow_cnt = rr.registers
                ts         = dt.datetime.utcnow()

                # Δt ≈ 0.1 s ➜ factor 600 para pasar a L/min
                flow_l_min = (flow_cnt * FLOW_K) * 600.0

                payload = {
                    "ts":   ts.isoformat(),
                    "lux":  lux,
                    "ph":   ph_raw / 100.0,
                    "ec":   ec_raw / 1000.0,
                    "flow": flow_l_min
                }

                # Redis – valor “live” para WebSocket
                await r.set("latest", json.dumps(payload))

                # TimescaleDB – histórico
                async with pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO sensor_log
                        (ts, lux, ph, ec, flow)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        ts, lux, ph_raw / 100.0, ec_raw / 1000.0, flow_l_min
                    )

                logging.info("Polled %s", payload)

            await asyncio.sleep(POLL)

if __name__ == "__main__":
    asyncio.run(main())
