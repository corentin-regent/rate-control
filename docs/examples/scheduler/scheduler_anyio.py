from anyio import create_task_group, current_time, run
from rate_control import Duration, FixedWindowCounter, RateController, Scheduler

async def request_print(controller: RateController, start_time: float) -> None:
    async with controller.request():
        print(f'Elapsed: {current_time() - start_time :.1f} seconds')

async def main() -> None:
    async with FixedWindowCounter(capacity=2, duration=Duration.SECOND) as bucket, \
            Scheduler(bucket) as scheduler, \
            create_task_group() as task_group:
        for _ in range(3):
            task_group.start_soon(request_print, scheduler, current_time())

run(main)
