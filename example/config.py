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
