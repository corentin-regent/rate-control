from asyncio import run
from rate_control import RateLimit, RateLimiter, UnlimitedBucket

async def main() -> None:
    async with UnlimitedBucket() as bucket:
        rate_limiter = RateLimiter(bucket, max_concurrency=1)

        with rate_limiter.hold():
            print('First request passes')
            try:
                rate_limiter.hold().__enter__()
            except RateLimit:
                print('Additional concurrent request is rejected')

        with rate_limiter.hold():
            print('New request passes when the first one is complete')

run(main())
