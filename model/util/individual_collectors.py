def create_collector(collector, name):
    collector.__name__ = name

    return collector


income = create_collector(lambda h: h.income, "income")
wealth = create_collector(lambda h: h.wealth, "wealth")
size = create_collector(lambda h: h.size, "size")
age = create_collector(lambda h: h.age, "age")
# house = create_collector(lambda h: h.contract.house, "house")
house_size = create_collector(lambda h: h.contract.house.size, "house size")
house_quality = create_collector(lambda h: h.contract.house.quality, "house quality")
size_per_person = create_collector(lambda h: h.contract.house.size / h.size, "size per person")
contract_cost = create_collector(lambda h: h.contract.get_costs(), "cost")
utility = create_collector(lambda h: h.current_utility(), "utility")
