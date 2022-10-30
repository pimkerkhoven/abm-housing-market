import random

from model.constants import MAX_AGE
from model.containers.agent_container import AgentContainer


class Households(AgentContainer):
    def tick(self, calibrate=False):
        households = list(self.values())
        random.shuffle(households)

        for household in households:
            if not calibrate:
                household.gain_wealth()

            household.update_contract()

            best_option = household.look_at_markets()
            household.act(best_option)

    def age_one_year(self):
        too_old = []
        for household in self.values():
            household.age += 1
            household.wait_list_time += 1

            if household.age >= MAX_AGE:
                too_old.append(household)

        self.remove_all(too_old)

    def assign_homelessness(self):
        for household in filter(lambda h: h.contract is None, self.values()):
            household.assign_homelessness()
