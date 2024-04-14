from asyncio import gather, get_running_loop, run
from rate_control import Duration, FixedWindowCounter, RateController, Scheduler

def current_time() -> float:
    loop = get_running_loop()
    return loop.time()

async def request_print(controller: RateController, start_time: float) -> None:
    async with controller.request():
        print(f'Elapsed: {current_time() - start_time :.1f} seconds')

async def main() -> None:
    async with FixedWindowCounter(capacity=2, duration=Duration.SECOND) as bucket, \
            Scheduler(bucket) as scheduler:
        await gather(*(
            request_print(scheduler, current_time())
            for _ in range(3)
        ))

run(main())
