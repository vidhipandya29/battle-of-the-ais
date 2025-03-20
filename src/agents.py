from enum import Enum


from mesa.discrete_space import FixedAgent




class State(Enum):
   SUSCEPTIBLE = 0
   #user has been exposed to but not interacted with AI content
   INFECTED = 1
   #user has been exposed to and interacted with AI content
   RESISTANT = 2
   #user has become immune - can see the ai-detection label




class VirusAgent(FixedAgent):
   def __init__(
       self,
       model,
       initial_state,
       ai_content_spread_chance,
       ai_check_frequency,
       recovery_chance,
       gain_resistance_chance,
       cell,
   ):
       super().__init__(model)


       self.state = initial_state


       self.ai_content_spread_chance = ai_content_spread_chance
       self.ai_check_frequency = ai_check_frequency
       self.recovery_chance = recovery_chance
       self.gain_resistance_chance = gain_resistance_chance
       self.cell = cell


   def try_to_infect_neighbors(self):
       for agent in self.cell.neighborhood.agents:
           if (agent.state is State.SUSCEPTIBLE) and (
               self.random.random() < self.ai_content_spread_chance
           ):
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
           self.random.random() < self.ai_check_frequency
       ):
           self.try_remove_infection()


   def step(self):
       if self.state is State.INFECTED:
           self.try_to_infect_neighbors()
       self.check_situation()



