try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
from multiprocessing import Process
import logging

log = logging.getLogger(__name__)

def processed(items, func, max_processes=5, max_queue=200, join=True,
              daemon=True):
    """
    Run a function ``func`` for each item in a generator ``items``
    in a set number of processes using a queue to manage the pending
    ``items``.

    :param items: The iterable of items to be processed.
    :param func: A function that accepts a single argument, an item
        from the iterable ``items``.
    :param num_processes: The number of processes to be spawned.
    :param max_queue: How many queued items should be read from the
        generator and put on the queue before processing is halted
        to allow the processing to catch up.
    :param join: If this is True, processed will wait for all processes
        to conclude; it will block until all processes are finished.
        If this is False, the the tasks won't block.
    :param daemon: Mark the worker processes as daemons in the
        operating system so that the program will terminate even if
        they are still running.
    """
    input_queue = Queue(maxsize=max_queue)
    output_queue = Queue(maxsize=max_queue)
    for item in items:
        input_queue.put(item, True)

    def wrapped_func(output_queue, item):
        try:
            func(item)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            output_queue.put(e)

    processes = []
    while not input_queue.empty():
        try:
            log.exception(output_queue.get_nowait())
        except Empty:
            pass
        while sum(1 for process in processes if process.is_alive()) >= max_processes:
            pass
        item = input_queue.get(True)
        processes.append(Process(target=wrapped_func, args = (output_queue, item,), daemon = daemon))
        processes[-1].start()
        input_queue.task_done()

    if join:
        while any(process.is_alive() for process in processes):
            pass
