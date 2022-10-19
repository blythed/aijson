# AI-JSONABLE

Parameter and settings tracking in Python3 for jsonable output.

## Installation

``` 
pip3 install ai-jsonable
```

## Philosophy

Saving and serializing in Python3 is supported by, for instance, `pickle` and `dill`. However, we believe that logging parameters in a Pythonic and flexible way is undersupported. Once a model or experiment has been executed, it should be easy to inspect which parameters were used. If the experiment is to be rerun or modified, it should be possible to do this with some simple overrides.

## Minimum working example

A minimal example is in `example/config.py`, which requires PyTorch and imports from `example/themod.py`.

To install do:

```
pip3 install torch
```

`example/themod.py`:

```python
from aijson.decorate import aijson
import torch


@aijson
class MyPyTorchModel(torch.nn.Module):
    def __init__(self, n_layers, n_hidden, n_input):
        super().__init__()
        self.rnn = torch.nn.GRU(n_hidden, n_hidden, n_layers)
        self.embed = torch.nn.Embedding(n_input, n_hidden)


@aijson
class MyCompose:
    def __init__(self, functions):
        self.functions = functions

    def __call__(self, x):
        for f in self.functions:
            x = f(x)
        return x

```

`example/config.py`:

```python
import json
from example.themod import MyPyTorchModel, MyCompose
from aijson import aijson, logging_context
from torch.nn import GRU

with logging_context() as lc:
    m = MyPyTorchModel(n_layers=1, n_hidden=512, n_input=64)
    rnn = aijson(GRU)(
        input_size=2,
        hidden_size=5,
    )
    n = MyCompose(functions=[m, m, 2, rnn])

    with open('mymodel.ai.json', 'w') as f:
        json.dump(lc, f)
```

In `example/themod.py` you can see that classes (and functions) whose parameter settings should be tracked are decorated with `@aijson`. Predefined functions (as in `torch.nn.XXX`) are similarly wrapped with `aijson(...)`. To create a single JSON-able logging instance in a Python dictionary, one uses the `logging_context` context manager. Having wired the model together in Python, all parameters chosen are recursively saved in the dictionary `lc`.

To run do:

```
python3 -m example.config
```

This should give output in `mymodel.ai.json`, which should look like this:

```json
{
  "var0": {
    "module": "example.themod",
    "caller": "MyPyTorchModel",
    "kwargs": {
      "n_layers": 1,
      "n_hidden": 512,
      "n_input": 64
    }
  },
  "var1": {
    "module": "torch.nn.modules.rnn",
    "caller": "GRU",
    "kwargs": {
      "input_size": 2,
      "hidden_size": 5
    }
  },
  "var2": {
    "module": "example.themod",
    "caller": "MyCompose",
    "kwargs": {
      "functions": [
        "$var0",
        "$var0",
        2,
        "$var1"
      ]
    }
  }
}
```

The JSON output is a dictionary representation of the build tree/ graph. If a parameter is JSON-able, then it will be directly saved in the `kwargs` subdictionary. Otherwise, it will be defined recursively. Hence the underlying assumption is that all parameters are either JSON-able or are Python objects whose parameters are JSON-able or are Python objects..., and so on. The base/ trunk node is the variable with highest index.

Once this output has been produced, it's possible to rebuild the object using the same parameters in the following way:

```python
import json
from aijson import build

with open('mymodel.ai.json') as f:
    cf = json.load(f)
    
rebuilt = build(cf)
```

This means that one doesn't need the code in `example/config.py` but only the items imported there (i.e. whatever is in `example/themod.py` and `torch` etc.).
