from asyncio import gather, get_running_loop, run
from rate_control import Duration, Scheduler, FixedWindowCounter

def current_time() -> float:
    loop = get_running_loop()
    return loop.time()

async def schedule_print(scheduler: Scheduler, start_time: float) -> None:
    async with scheduler.schedule():
        print(f'Elapsed: {current_time() - start_time :.1f} seconds')

async def main() -> None:
    async with FixedWindowCounter(capacity=2, duration=Duration.SECOND) as bucket, \
            Scheduler(bucket) as scheduler:
        await gather(*(
            schedule_print(scheduler, current_time())
            for _ in range(3)
        ))

run(main())
