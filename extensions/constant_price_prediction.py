from model.util.injector import inject


@inject("rules")
def _get_market_prices_constant(self, data, rules):
    return [rules.constant_price] * len(data)