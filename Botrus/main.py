from contributor import Contributor
from user import User
import asyncio



async def main():
    newloop = asyncio.new_event_loop()
    c = Contributor("")
    asyncio.run_coroutine_threadsafe(c.start(), newloop)
    asyncio.sleep(1)
    u = User()
    await u.start("127.0.0.1")


asyncio.run(main())
