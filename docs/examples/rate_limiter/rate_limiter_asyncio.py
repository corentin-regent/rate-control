from asyncio import run
from rate_control import Duration, RateLimit, RateLimiter
from rate_control.buckets import FixedWindowCounter

async def main() -> None:
    async with FixedWindowCounter(capacity=2, duration=Duration.MINUTE) as bucket:
        rate_limiter = RateLimiter(bucket)

        for _ in range(3):
            try:
                with rate_limiter.hold():
                    print('Request executed')
            except RateLimit:
                print('Request rejected')

run(main())
