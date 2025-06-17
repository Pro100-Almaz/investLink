import asyncio
import threading

from src.scheduler.tasks import run_scheduler


def start_scheduler() -> None:
    def run_scheduler_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_scheduler())

    scheduler_thread = threading.Thread(target=run_scheduler_in_thread, daemon=True)
    scheduler_thread.start() 