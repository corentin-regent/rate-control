from trio import current_time, open_nursery, run
from rate_control import Duration, Scheduler
from rate_control.buckets import FixedWindowCounter

async def schedule_print(scheduler: Scheduler, start_time: float) -> None:
    async with scheduler.schedule():
        print(f'Elapsed: {current_time() - start_time :.1f} seconds')

async def main() -> None:
    async with FixedWindowCounter(capacity=2, duration=Duration.SECOND) as bucket, \
            Scheduler(bucket) as scheduler, \
            open_nursery() as nursery:
        for _ in range(3):
            nursery.start_soon(schedule_print, scheduler, current_time())

run(main)
