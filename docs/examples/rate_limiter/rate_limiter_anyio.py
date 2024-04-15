from anyio import run
from rate_control import Duration, FixedWindowCounter, RateLimit, RateLimiter

async def main() -> None:
    bucket = FixedWindowCounter(capacity=2, duration=Duration.MINUTE)
    async with RateLimiter(bucket) as rate_limiter:
        for _ in range(3):
            try:
                async with rate_limiter.request():
                    print('Request executed')
            except RateLimit:
                print('Request rejected')

run(main)
