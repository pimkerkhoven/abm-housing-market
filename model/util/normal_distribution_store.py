from model.util.rng import rng


class NormalDistributionStore:
    def __init__(self, mean, sigma, num_values=100_000):
        self.mean = mean
        self.sigma = sigma
        self.num_values = num_values

        self.index = 0
        self.values = rng.normal(mean, sigma, num_values)

    def next(self):
        if self.index >= len(self.values):
            self.index = 0
            # print("renew")
            self.values = rng.normal(self.mean, self.sigma, self.num_values)

        value = self.values[self.index]
        self.index += 1

        return value
