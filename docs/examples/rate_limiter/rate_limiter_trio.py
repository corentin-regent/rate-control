from trio import run
from rate_control import Duration, FixedWindowCounter, RateLimit, RateLimiter

async def main() -> None:
    async with FixedWindowCounter(capacity=2, duration=Duration.MINUTE) as bucket:
        rate_limiter = RateLimiter(bucket)

        for _ in range(3):
            try:
                async with rate_limiter.request():
                    print('Request executed')
            except RateLimit:
                print('Request rejected')

run(main)
