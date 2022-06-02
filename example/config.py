from example.themod import MyPyTorchModel, MyCompose

m = MyPyTorchModel(1, 512, 64)
n = MyCompose([m, m, 2])
