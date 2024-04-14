from asyncio import run
from rate_control import Duration, RateLimit, RateLimiter, FixedWindowCounter

def normal_request(rate_limiter: RateLimiter) -> None:
    with rate_limiter.hold():  # weight defaults to 1
        print('Executed normal request')

def heavy_request(rate_limiter: RateLimiter) -> None:
    with rate_limiter.hold(2):
        print('Executed heavy request')

async def main() -> None:
    async with FixedWindowCounter(capacity=3, duration=Duration.HOUR) as bucket:
        rate_limiter = RateLimiter(bucket)
        heavy_request(rate_limiter)
        try:
            heavy_request(rate_limiter)
        except RateLimit:
            print('Heavy request got rate limited')
        normal_request(rate_limiter)

run(main())
