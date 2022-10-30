from model.agents.bank import Bank
from model.agents.government import Government
from model.constants import MONTHS
from model.util.injector import inject


class BonusBank(Bank):
    @inject("rules")
    def max_bid(self, household, rules):
        max_value = super().max_bid(household)

        if rules.buy_bonus["deserve?"](household):
            return max_value + rules.buy_bonus["value"]

        return max_value

    @inject("rules", "government")
    def value_to_monthly_payment(self, value, household, rules, government, buying=False):
        if rules.buy_bonus["deserve?"](household):
            if buying:
                government.bonuses_rewarded += 1

            value -= rules.buy_bonus["value"]

        return super().value_to_monthly_payment(value, household)


class BonusGovernment(Government):
    def __init__(self, initial_tax_rate=0):
        super().__init__(initial_tax_rate)
        self.bonuses_rewarded = 0

    @inject("households", "rules")
    def set_new_tax_rate(self, households, rules):
        total_rent_allowance_per_month = sum([self.determine_rent_allowance(h, h.contract.get_costs(), h.contract.house)
                                              for h in households.values()])
        total_income_per_month = sum([h.income for h in households.values() if h.income > 0])
        total_bonus_amount_per_month = (self.bonuses_rewarded * rules.buy_bonus['value']) / len(MONTHS)

        self.tax_rate = (total_rent_allowance_per_month + total_bonus_amount_per_month) / total_income_per_month
        self.bonuses_rewarded = 0




