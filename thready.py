try:
    from queue import Queue
except ImportError:
    from Queue import Queue
from threading import Thread
import logging

log = logging.getLogger(__name__)


def threaded(items, func, num_threads=5, max_queue=200, join=True,
             daemon=True):
    """
    Run a function ``func`` for each item in a generator ``items``
    in a set number of threads using a queue to manage the pending
    ``items``.

    :param items: The iterable of items to be processed.
    :param func: A function that accepts a single argument, an item
        from the iterable ``items``.
    :param num_threads: The number of threads to be spawned. Values
        ranging from 5 to 40 have shown useful, based on the amount
        of I/O involved in each task.
    :param max_queue: How many queued items should be read from the
        generator and put on the queue before processing is halted
        to allow the processing to catch up.
    :param join: If this is True, threaded will wait for all threads
        to conclude; it will block until all threads are finished.
        If this is False, the the tasks won't block.
    :param daemon: Mark the worker threads as daemons in the
        operating system so that the program will terminate even if
        they are still running.
    """
    def queue_consumer():
        while True:
            try:
                item = queue.get(True)
                func(item)
            except Exception as e:
                log.exception(e)
            except KeyboardInterrupt:
                raise
            except:
                pass
            finally:
                queue.task_done()

    queue = Queue(maxsize=max_queue)

    for i in range(num_threads):
        t = Thread(target=queue_consumer)
        t.daemon = daemon
        t.start()

    for item in items:
        queue.put(item, True)

    if join:
        queue.join()
