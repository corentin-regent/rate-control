from trio import run, sleep
from trio.lowlevel import checkpoint
from rate_control import Duration, FixedWindowCounter, RateLimit, RateLimiter

async def main() -> None:
    first_bucket = FixedWindowCounter(2, Duration.SECOND)
    second_bucket = FixedWindowCounter(3, 2 * Duration.SECOND)
    async with RateLimiter(first_bucket, second_bucket) as rate_limiter:
        async with rate_limiter.request():
            print('First request passes')
        async with rate_limiter.request():
            print('Second request passes')

        try:
            async with rate_limiter.request(): ...
        except RateLimit:
            print('First bucket is empty')

        await sleep(Duration.SECOND)
        await checkpoint()  # yield control to the buckets
        async with rate_limiter.request():
            print('New request passes after replenishment')

        try:
            async with rate_limiter.request(): ...
        except RateLimit:
            print('Now second bucket is empty')

run(main)
