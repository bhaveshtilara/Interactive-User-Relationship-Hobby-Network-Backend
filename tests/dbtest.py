import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/cybernauts_db')
    print("✅ Connected successfully:", conn)
    await conn.close()

asyncio.run(test())
