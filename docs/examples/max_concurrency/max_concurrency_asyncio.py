from asyncio import run
from rate_control import RateLimit, RateLimiter, UnlimitedBucket

async def main() -> None:
    async with UnlimitedBucket() as bucket:
        rate_limiter = RateLimiter(bucket, max_concurrency=1)

        async with rate_limiter.request():
            print('First request passes')
            try:
                async with rate_limiter.request(): ...
            except RateLimit:
                print('Additional concurrent request is rejected')

        async with rate_limiter.request():
            print('New request passes when the first one is complete')

run(main())
