import collections
import random

import pandas as pd

from model.agents.house import RentalHouse, BuyHouse
from model.constants import MIN_HOUSE_SIZE, MAX_HOUSE_SIZE, MIN_HOUSE_QUALITY, MAX_HOUSE_QUALITY
from model.containers.houses import Houses

HouseSizeGroup = collections.namedtuple('HouseSizeGroup', ['min_m2', 'max_m2'])

# Note: max size in data is 10_000, here we set it to 1_000.
#  Same for min 2 in data here set to 10
HOUSE_SIZE_GROUPS = [HouseSizeGroup(MIN_HOUSE_SIZE, 15), HouseSizeGroup(15, 50), HouseSizeGroup(50, 75),
                     HouseSizeGroup(75, 100), HouseSizeGroup(100, 150), HouseSizeGroup(150, 250),
                     HouseSizeGroup(250, 500), HouseSizeGroup(500, MAX_HOUSE_SIZE)]


class HouseFactory:
    def __init__(self):
        self.houses_by_size_per_year = pd.read_csv("data/houses_by_size_per_year.csv", sep=";")
        self.house_purpose_per_year = pd.read_csv("data/house_purpose_data.csv", sep=";")

    def create_houses(self, year, initial_portion_houses_for_rent, scale_factor=1):
        data_for_year = self.houses_by_size_per_year[
                            self.houses_by_size_per_year["Year"] == year].iloc[:, 2:]
        row_index_for_year = data_for_year.index[0]

        purpose_data_for_year = self.house_purpose_per_year[
                                    self.house_purpose_per_year["Year"] == year].iloc[:, 2:]
        purpose_total = purpose_data_for_year.sum(axis=1).iloc[0] if initial_portion_houses_for_rent is None else 100
        purpose_buy = purpose_data_for_year.iloc[0, 0] if initial_portion_houses_for_rent is None \
            else 100 * (1 - initial_portion_houses_for_rent)

        houses = Houses()

        for (i, header) in enumerate(data_for_year):
            house_size_group = HOUSE_SIZE_GROUPS[i]
            scaled_number_of_households_in_group = round(data_for_year.loc[row_index_for_year, header] / scale_factor)

            for _ in range(scaled_number_of_households_in_group):
                size = random.randint(house_size_group.min_m2, house_size_group.max_m2 - 1)
                quality = random.randint(MIN_HOUSE_QUALITY, MAX_HOUSE_QUALITY)
                if random.randint(0, purpose_total) < purpose_buy:
                    houses.add(BuyHouse(size, quality))
                else:
                    houses.add(RentalHouse(size, quality))

        return houses
