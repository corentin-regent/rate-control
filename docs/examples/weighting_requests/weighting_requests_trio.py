from trio import run
from rate_control import Duration, FixedWindowCounter, RateController, RateLimit, RateLimiter

async def normal_request(controller: RateController) -> None:
    async with controller.request():  # weight defaults to 1
        print('Executed normal request')

async def heavy_request(rate_limiter: RateLimiter) -> None:
    async with rate_limiter.request(2):
        print('Executed heavy request')

async def main() -> None:
    bucket = FixedWindowCounter(capacity=3, duration=Duration.HOUR)
    async with RateLimiter(bucket) as rate_limiter:
        await heavy_request(rate_limiter)
        try:
            await heavy_request(rate_limiter)
        except RateLimit:
            print('Heavy request got rate limited')
        await normal_request(rate_limiter)

run(main)
