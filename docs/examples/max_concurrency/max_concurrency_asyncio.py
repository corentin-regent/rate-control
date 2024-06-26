from asyncio import run
from rate_control import RateLimit, RateLimiter

async def main() -> None:
    async with RateLimiter(max_concurrency=1) as rate_limiter:
        async with rate_limiter.request():
            print('First request passes')
            try:
                async with rate_limiter.request(): ...
            except RateLimit:
                print('Additional concurrent request is rejected')

        async with rate_limiter.request():
            print('New request passes when the first one is complete')

run(main())
