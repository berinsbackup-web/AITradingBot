import asyncio

async def safe_execute(coro, retries=3, logger=None):
    for attempt in range(1, retries + 1):
        try:
            return await coro
        except Exception as exc:
            if logger:
                logger.error("Execution error: %s [Retry %d/%d]", exc, attempt, retries)
            await asyncio.sleep(0.5 * attempt)
    if logger:
        logger.error("Max retries exceeded for %s", coro)
    raise RuntimeError("Operation failed after max retries")
