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
