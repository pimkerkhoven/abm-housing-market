class AgentContainer:
    def __init__(self):
        self._agents = {}

    def add(self, agent):
        self._agents[agent.id] = agent

    def update(self, agent):
        self.add(agent)

    def remove_all(self, agents):
        for agent in agents:
            self.remove(agent)

    def remove(self, agent):
        agent.remove()
        self._agents.pop(agent.id)

    def values(self):
        return self._agents.values()

    def __getitem__(self, key):
        return self._agents[key]

    def __len__(self):
        return len(self._agents)