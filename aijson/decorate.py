from collections import defaultdict
from functools import wraps
import inspect
import json


class AiJson:
    def __init__(self):
        self.reset()
        self.vanilla = False

    def reset(self):
        self.graph = {}
        self.variables = defaultdict(lambda: f'var{len(self.variables)}')

    def substitute(self, d):
        if not (isinstance(d, dict) or isinstance(d, list)):
            if any([x == d for x in self.graph.values()]):
                return d
            try:
                json.dumps(d)
                return d
            except Exception as e:
                id_ = id(d)
                var = self.variables[id_]
                if var not in self.graph:
                    raise Exception(f'found undecorated, non jsonable output: {d}') from e
                return f'${var}'

        if isinstance(d, dict):
            out = {}
            for k, v in d.items():
                out[k] = self.substitute(v)
            return out
        elif isinstance(d, list):
            return [self.substitute(x) for x in d]

    def __call__(self, f):
        @wraps(f)
        def wrapped(**kwargs):
            if self.vanilla:
                return f(**kwargs)
            kwargs_ = self.substitute(kwargs)
            out = f(**kwargs)

            id_ = id(out)
            if self.variables[id_] in self.graph:
                self.graph[self.variables[id_]] = {
                    'module': f.__module__,
                    'caller': f.__name__,
                    'kwargs': kwargs_
                }
            return out

        def _myinit(aself, **kwargs):
            if self.vanilla:
                return f._old_init(aself, **kwargs)
            kwargs_ = self.substitute(kwargs)
            f._old_init(aself, **kwargs)
            id_ = id(aself)
            self.graph[self.variables[id_]] = {
                'module': f.__module__,
                'caller': f.__name__,
                'kwargs': kwargs_
            }
            return

        if inspect.isclass(f):
            f._old_init = f.__init__
            f.__init__ = wraps(f._old_init)(_myinit)
            return f
        else:
            return wrapped


aijson = AiJson()
