from math import cos, pi

class Problem:
    def __init__(self):
        raise NotImplementedError("Abstract class")

    def evaluate(self, x):
        raise NotImplementedError("Abstract method")
    
    def name(self):
        raise NotImplementedError("Abstract method")

class Rastrigin(Problem):
    def __init__(self, n_dim, a=10.0):
        assert n_dim > 0
        assert a != 0

        self.n_dim = n_dim
        self.a = a

    def evaluate(self, x):
        assert len(x) == self.n_dim
        
        return self.a * len(x) + sum([x[i]**2 - self.a * cos(2*pi*x[i]) for i in range(len(x))])

    def name(self):
        return "RAST"
