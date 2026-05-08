import time 
import asyncio

async def count():
    print('One')
    await asyncio.sleep(1) # <-- asyncio.sleep()
    print('Two')
    await asyncio.sleep(1) # <--

async def main():
    # ---- asyncio.gather()
    await asyncio.gather(count(), count(), count())


start = time.perf_counter()
# ---- asyncio.run()
asyncio.run(main())
elapsed = time.perf_counter() - start
print(f'{__file__} 실행 시간 {elapsed:0.2f} 초.')
