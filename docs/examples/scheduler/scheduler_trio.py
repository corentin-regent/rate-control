from trio import current_time, open_nursery, run
from rate_control import Duration, FixedWindowCounter, RateController, Scheduler

async def request_print(controller: RateController, start_time: float) -> None:
    async with controller.request():
        print(f'Elapsed: {current_time() - start_time :.1f} seconds')

async def main() -> None:
    bucket = FixedWindowCounter(capacity=2, duration=Duration.SECOND)
    async with Scheduler(bucket) as scheduler, open_nursery() as nursery:
        for _ in range(3):
            nursery.start_soon(request_print, scheduler, current_time())

run(main)
