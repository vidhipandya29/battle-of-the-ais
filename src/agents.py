from enum import Enum

from mesa.space import DiscreteSpace

from mesa.discrete_space import FixedAgent


class State(Enum):
    SUSCEPTIBLE = 0
    # user has been exposed to but not interacted with AI content
    INFECTED = 1
    # user has been exposed to and interacted with AI content
    RESISTANT = 2
    # user has become immune - can see the ai-detection label


class VirusAgent(FixedAgent):
    def __init__(
        self,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        recovery_chance,
        gain_resistance_chance,
        # resistance_loss_threshold,
        # decrease_resistance_chance,
        cell,
    ):
        super().__init__(model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.cell = cell


        # self.resistance_loss_threshold = 1  # Hardcoded value
        # self.decrease_resistance_chance = 1  # Hardcoded value

    def try_to_infect_neighbors(self):
        for agent in self.cell.neighborhood.agents:
            if (agent.state is State.SUSCEPTIBLE) and (
                self.random.random() < self.virus_spread_chance
            ):
                # print("Hi")
                agent.state = State.INFECTED

            #reinfect if neighbours are infected   
            elif agent.state is State.RESISTANT:  # Only try to reinfect resistant agents
                infected_neighbors = 0
                for neighbor in agent.cell.neighborhood.agents:
                    if neighbor.state is State.INFECTED:
                        infected_neighbors += 1
                if infected_neighbors >= 1 and self.random.random() < 0.8:
                    print("Reinfected!")
                    agent.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.recovery_chance:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def check_situation(self):
        if (self.state is State.INFECTED) and (
            self.random.random() < self.virus_check_frequency
        ):
            self.try_remove_infection()

    def step(self):
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        elif self.state is State.RESISTANT:
            self.try_to_infect_neighbors()
        self.check_situation()