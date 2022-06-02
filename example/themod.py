from aijson import Jsonable
import io
import torch


class MyModule(torch.nn.Module):
    ext = '.pt'

    def __init__(self):
        super().__init__()

    @property
    def data(self):
        f = io.BytesIO()
        torch.save(self.state_dict(), f)
        return f.getvalue()

    @data.setter
    def data(self, value):
        f = io.BytesIO()
        f.write(value)
        f.seek(0)
        self.load_state_dict(torch.load(f))


class MyPyTorchModel(MyModule, Jsonable):
    def __init__(self, n_layers, n_hidden, n_input):
        Jsonable.__init__(self, n_layers=n_layers, n_hidden=n_hidden, n_input=n_input)
        torch.nn.Module.__init__(self)
        self.rnn = torch.nn.GRU(n_hidden, n_hidden, n_layers)
        self.embed = torch.nn.Embedding(n_input, n_hidden)


class MyCompose(Jsonable):
    def __init__(self, functions):
        super().__init__(functions=functions)
        self.functions = functions

    def __call__(self, x):
        for f in self.functions:
            x = f(x)
        return x
