from trio import run, sleep
from trio.lowlevel import checkpoint
from rate_control import BucketGroup, Duration, RateLimit, RateLimiter
from rate_control.buckets import FixedWindowCounter

async def main() -> None:
    first_bucket = FixedWindowCounter(2, Duration.SECOND)
    second_bucket = FixedWindowCounter(3, 2 * Duration.SECOND)
    async with BucketGroup(first_bucket, second_bucket) as bucket_group:
        rate_limiter = RateLimiter(bucket_group)

        with rate_limiter.hold():
            print('First request passes')
        with rate_limiter.hold():
            print('Second request passes')

        try:
            rate_limiter.hold().__enter__()
        except RateLimit:
            print('First bucket is empty')

        await sleep(Duration.SECOND)
        await checkpoint()  # yield control to the buckets
        with rate_limiter.hold():
            print('New request passes after replenishment')

        try:
            rate_limiter.hold().__enter__()
        except RateLimit:
            print('Now second bucket is empty')

run(main)
