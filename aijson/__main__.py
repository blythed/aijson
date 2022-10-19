import click
import json
import os
from pygments import highlight, lexers, formatters
import re
from aijson.build import build as _build


def parse_inputs(x):
    groups = re.finditer('"([^\']+)"', x)
    reference = {}
    for i, g in enumerate(groups):
        x = x.replace(g.group(), f'#{i}')
        reference[f'#{i}'] = g.groups()[0]
    my_dict = dict([x.split('=') for x in x.split(',')])
    for k, val in my_dict.items():
        if val.isnumeric():
            my_dict[k] = eval(val)
        elif val.startswith('#'):
            my_dict[k] = reference[val]
        elif val in {'true', 'True', 'false', 'False'}:
            my_dict[k] = val.lower() == 'true'
        elif '+' in val:
            val = val.split('+')
            val = [x for x in val if x]
            val = [eval(x) if x.isnumeric() else x for x in val]
            my_dict[k] = val
    return my_dict


class KeyValuePairs(click.ParamType):
    """Convert to key value pairs"""
    name = "key-value-pairs"

    def convert(self, value, param, ctx):
        """
        Convert to key value pairs

        :param value: value
        :param param: parameter
        :param ctx: context
        """
        if not value.strip():
            return {}
        try:
            my_dict = parse_inputs(value)
            for k, v in my_dict.items():
                if isinstance(v, str) and '$' in v:
                    matches = re.findall('\$([A-Za-z\_0-9]+)', v)
                    for m in matches:
                        try:
                            my_dict[k] = my_dict[k].replace(f'${m}', os.environ[m])
                        except KeyError:
                            raise Exception('key values referred to environment variable which did'
                                            ' not exist')
            return my_dict
        except TypeError:
            self.fail(
                "expected string for key-value-pairs() conversion, got "
                f"{value!r} of type {type(value).__name__}",
                param,
                ctx,
            )
        except ValueError:
            self.fail(f"{value!r} is not a valid key-value-pair", param, ctx)


@click.group
def cli():
    ...


def set_overrides(d, overrides):
    for k in overrides:
        var, key = k.split('.')
        d[var]['kwargs'][key] = overrides[k]
    return d


@cli.command()
@click.argument('path')
@click.option('--overrides', default=None)
@click.option('--node', default=None)
@click.option('--output', default=None)
@click.option('--verbose/--no-verbose', default=True)
def build(path, overrides, node, output, verbose):
    with open(path) as f:
        cf = json.load(f)
    if overrides is not None:
        cf = set_overrides(cf, overrides)
    if overrides is not None:
        with open(output, 'w') as f:
            json.dump(cf, f)
    if verbose:
        print('building this graph:')
        show = json.dumps(cf, indent=2)
        colorful_json = highlight(show, lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)
    out = _build(cf, node=node)
    print(out)


if __name__ == '__main__':
    cli()