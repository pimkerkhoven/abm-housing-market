from model.constants import MONTHS
from model.util.contracts import NoHouse
from model.util.normal_distribution_store import NormalDistributionStore


class Utility:
    def __init__(self, money_weight, house_size_weight, house_quality_weight,
                 movement_cost=0.0, rum_mean=0, rum_std_dev=1):
        self.money_weight = money_weight
        self.house_size_weight = house_size_weight
        self.house_quality_weight = house_quality_weight
        self.movement_cost = movement_cost

        self.normal_distribution_store = NormalDistributionStore(rum_mean, rum_std_dev)

    def __call__(self, household, house, cost):
        pass


# class LinearUtility(Utility):
#     def __call__(self, household, house, cost):
#         rum = self.normal_distribution_store.next()
#         movement_cost = self.movement_cost if not house == household.contract.house else 0
#
#         return self.money_weight * household.left_over_money(cost) \
#                + self.house_size_weight * (house.size / household.size) \
#                + self.house_quality_weight * house.quality \
#                - movement_cost \
#                + rum
#
#
# class RootSizeUtility(Utility):
#     def __call__(self, household, house, cost):
#         rum = self.normal_distribution_store.next()
#         movement_cost = self.movement_cost if not house == household.contract.house else 0
#
#         return self.money_weight * household.left_over_money(cost) \
#                + self.house_size_weight * (house.size / household.size) ** 0.5 \
#                + self.house_quality_weight * house.quality \
#                - movement_cost \
#                + rum
#
#
# class MultiplyQualitySizeUtility(Utility):
#     def __call__(self, household, house, cost):
#         rum = self.normal_distribution_store.next()
#         movement_cost = self.movement_cost if not house == household.contract.house else 0
#         #
#         # print(
#         #     self.money_weight * household.left_over_money(cost),
#         #     self.house_size_weight * (house.size / household.size)
#         #     * self.house_quality_weight * house.quality,
#         #     movement_cost,
#         #     rum
#         # )
#
#         return self.money_weight * household.left_over_money(cost) \
#                + self.house_size_weight * (house.size / household.size) \
#                * self.house_quality_weight * house.quality \
#                - movement_cost \
#                + rum


class MultiplyQualityRootSizeUtility(Utility):
    def __call__(self, household, house, cost):
        rum = self.normal_distribution_store.next()

        movement_cost = 0
        if not house == household.contract.house and not isinstance(household.contract.house, NoHouse):
            movement_cost = self.movement_cost
            if household.contract.run_time > 0:
                movement_cost = movement_cost * (len(MONTHS) / household.contract.run_time)

        homeless_penalty = 5 if isinstance(household.contract.house, NoHouse) else 0

        return self.money_weight * household.left_over_money(cost, house) \
               + self.house_size_weight * (house.size / household.size) ** 0.5 \
               * self.house_quality_weight * house.quality \
               - movement_cost \
               - homeless_penalty\
               + rum


# class MultiplyQualityRootSizeUtilityAlternativeMovementCost(Utility):
#     def __call__(self, household, house, cost):
#         rum = self.normal_distribution_store.next()
#
#         movement_cost = self.movement_cost if not house == household.contract.house else 0
#
#         return self.money_weight * household.left_over_money(cost) \
#                + self.house_size_weight * (house.size / household.size) ** 0.5 \
#                * self.house_quality_weight * house.quality \
#                - movement_cost \
#                + rum


default_utility_function = MultiplyQualityRootSizeUtility(money_weight=0.0005, house_size_weight=0.1,
                                                          house_quality_weight=1, movement_cost=1.5)



