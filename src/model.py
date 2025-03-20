import math


import networkx as nx


import mesa
from mesa import Model
from mesa.discrete_space import CellCollection, Network
from mesa.examples.basic.virus_on_network.agents import State, VirusAgent


def number_state(model, state):
   return sum(1 for a in model.grid.all_cells.agents if a.state is state)

def number_infected(model):
   return number_state(model, State.INFECTED)


def number_susceptible(model):
   return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
   return number_state(model, State.RESISTANT)

class VirusOnNetwork(Model):


   def __init__(
       self,
   ):
       super().__init__(seed=seed)
    

       num_nodes=100 
       avg_node_degree=3
       initial_outbreak_size=1
       virus_spread_chance=0.37
       virus_check_frequency=0.5
       recovery_chance=0.3
       gain_resistance_chance=0.5

       seed=None,
       prob = avg_node_degree / num_nodes
       
       graph = nx.erdos_renyi_graph(n=100, p=prob)
       self.grid = Network(graph, capacity=1, random=self.random)


       self.initial_outbreak_size = 30


       self.datacollector = mesa.DataCollector(
           {
               "Interacted": number_infected,
               "Viewed": number_susceptible,
               "Labelled Content": number_resistant,
               "R over S": self.resistant_susceptible_ratio,
           }
       )


       VirusAgent.create_agents(
           self,
           num_nodes,
           State.SUSCEPTIBLE,
           virus_spread_chance,
           virus_check_frequency,
           recovery_chance,
           gain_resistance_chance,
           list(self.grid.all_cells),
       )


       # Infect some nodes
       infected_nodes = CellCollection(
           self.random.sample(list(self.grid.all_cells), self.initial_outbreak_size),
           random=self.random,
       )
       for a in infected_nodes.agents:
           a.state = State.INFECTED


       self.running = True
       self.datacollector.collect(self)


   def resistant_susceptible_ratio(self):
       try:
           return number_state(self, State.RESISTANT) / number_state(
               self, State.SUSCEPTIBLE
           )
       except ZeroDivisionError:
           return math.inf


   def step(self):
       self.agents.shuffle_do("step")
       # collect data
       self.datacollector.collect(self)