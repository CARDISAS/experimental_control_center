import asyncio, os, datetime as dt, json, logging
from pymodbus.client import AsyncModbusTcpClient
import asyncpg
import redis.asyncio as redis

logging.basicConfig(level=logging.INFO)

MCU_HOST = os.getenv("MCU_HOST", "esp32.local")
MCU_PORT = int(os.getenv("MCU_PORT", "502"))
POLL = float(os.getenv("POLL_INTERVAL", "1.0"))
PG_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@db:5432/postgres")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

async def main():
    r = redis.from_url(REDIS_URL)
    pool = await asyncpg.create_pool(PG_DSN)
    async with AsyncModbusTcpClient(MCU_HOST, MCU_PORT) as client:
        while True:
            rr = await client.read_holding_registers(0, 3, unit=1)
            if rr.isError():
                logging.error("Modbus error %s", rr)
            else:
                lux, ph_raw, ec_raw = rr.registers
                timestamp = dt.datetime.utcnow()
                data = dict(ts=timestamp.isoformat(), lux=lux, ph=ph_raw/100, ec=ec_raw/1000)
                # Write to Redis
                await r.set("latest", json.dumps(data))
                # Write to Timescale
                async with pool.acquire() as conn:
                    await conn.execute(
                        "INSERT INTO sensor_log(ts, lux, ph, ec) VALUES ($1,$2,$3,$4)",
                        timestamp, lux, ph_raw/100, ec_raw/1000
                    )
                logging.info("Polled %s", data)
            await asyncio.sleep(POLL)

if __name__ == "__main__":
    asyncio.run(main())
