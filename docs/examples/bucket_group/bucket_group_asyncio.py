from asyncio import run, sleep
from rate_control import BucketGroup, Duration, FixedWindowCounter, RateLimit, RateLimiter

async def main() -> None:
    first_bucket = FixedWindowCounter(2, Duration.SECOND)
    second_bucket = FixedWindowCounter(3, 2 * Duration.SECOND)
    async with BucketGroup(first_bucket, second_bucket) as bucket_group:
        rate_limiter = RateLimiter(bucket_group)

        async with rate_limiter.request():
            print('First request passes')
        async with rate_limiter.request():
            print('Second request passes')

        try:
            async with rate_limiter.request(): ...
        except RateLimit:
            print('First bucket is empty')

        await sleep(Duration.SECOND)
        await sleep(0)  # yield control to the buckets
        async with rate_limiter.request():
            print('New request passes after replenishment')

        try:
            async with rate_limiter.request(): ...
        except RateLimit:
            print('Now second bucket is empty')

run(main())
