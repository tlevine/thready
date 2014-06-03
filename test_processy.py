try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import processy


def test_processed():
    import processy
    results = Queue()
    def f(fn):
        open(fn, 'w').write('Hi')
    processy.processed(['/tmp/a', '/tmp/b'], f)
    for fn in ['/tmp/a', '/tmp/b']:
        with open(fn) as fp:
            assert fp.read() == 'Hi', fn

def test_error():
    import processy
    def f(i):
        raise ValueError
    processy.processed(range(10), f)
