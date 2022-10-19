import importlib
from aijson.decorate import aijson


def find_variables(item):
    if isinstance(item, str) and item.startswith('$'):
        return [item[1:]]
    if isinstance(item, dict):
        vars = []
        for k, v in item.items():
            vars.extend(find_variables(v))
        return vars
    if isinstance(item, list):
        vars = []
        for x in item:
            vars.extend(find_variables(x))
        return vars
    return []


def replace_variables(item, graph):
    if isinstance(item, str) and item.startswith('$'):
        return graph[item[1:]]

    if isinstance(item, dict):
        out = {}
        for k, v in item.items():
            out[k] = replace_variables(v, graph)
        return out

    if isinstance(item, list):
        return [replace_variables(x, graph) for x in item]

    return item


def build(graph, node=None):
    if node is None:
        aijson.vanilla = True
        node = max(list(graph.keys()), key=lambda x: int(x[3:]))
    vars_ = find_variables(graph[node]['kwargs'])
    for var in vars_:
        if isinstance(graph[var], dict) and 'kwargs' in graph[var] and 'module' in graph[var] \
           and 'caller' in graph[var]:
            build(graph, node=var)

    kwargs = replace_variables(graph[node]['kwargs'], graph)
    module = importlib.import_module(graph[node]['module'])
    caller = getattr(module, graph[node]['caller'])

    out = caller(**kwargs)
    graph[node] = out
    if node is None:
        aijson.vanilla = False
    return out
