from contextlib import contextmanager

from django.core.cache import cache

# get_ifcb_dashboard_data, get_ifcb_dashboard_data_high_priority,
# reset_ifcb_dataset_data, and recalculate_metrics all read/write the same
# Bin/AutoclassScore rows and hit the same dashboard API, so only one of
# them may run at a time across all Celery workers.
INGESTION_LOCK_KEY = "ifcb_datasets:ingestion_lock"


@contextmanager
def ingestion_lock(timeout):
    """
    Non-blocking distributed lock shared by the IFCB ingestion tasks.

    `timeout` is a safety-net TTL, not an expected run time: if a worker is
    killed (e.g. OOM) while holding the lock, Python's `finally` never runs,
    so the lock would otherwise stay held until this many seconds pass.
    Pick it high enough to comfortably cover a normal run of the calling
    task, but no higher than necessary, so a crash self-heals reasonably
    soon instead of blocking every other ingestion task in the meantime.

    Usage:
        with ingestion_lock(timeout=3600) as acquired:
            if not acquired:
                return  # another ingestion task is already running
            ...
    """
    lock = cache.lock(INGESTION_LOCK_KEY, timeout=timeout)
    acquired = lock.acquire(blocking=False)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()
