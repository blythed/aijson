import contextlib
from aijson.decorate import aijson


@contextlib.contextmanager
def logging_context():
    aijson.reset()
    yield aijson.graph
    aijson.reset()
