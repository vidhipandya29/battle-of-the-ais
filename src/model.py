from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx

class ContentAgent(Agent):
    """An agent representing a social media user."""
    
    def __init__(self, unique_id, model, agent_type="user"):
        super().__init__(unique_id, model)
        self.agent_type = agent_type  # "user", "generator", or "detector"
        self.exposed = False  # Whether the agent has been exposed to deepfake content
        self.labeled = False  # Whether the content has been labeled as AI-generated
        self.pos = None  # Will be set when placed on grid
        
        # Add AI battle attributes
        if agent_type == "generator":
            self.effectiveness = 1.0  # Start at full effectiveness
            self.neutralized = False  # Whether the generator has been neutralized
            self.evasion_skill = self.random.random() * 0.5  # Chance to evade detection
        
        if agent_type == "detector":
            self.detection_power = 1.0  # Initial detection power
            self.ai_victories = 0  # Counter for AIs neutralized
        
    def step(self):
        """Agent's behavior during each step of the simulation."""
        # Skip if position is not set
        if self.pos is None:
            return
            
        if self.agent_type == "generator":
            # Skip if neutralized
            if hasattr(self, 'neutralized') and self.neutralized:
                return
                
            # Generators create and spread deepfake content
            effectiveness_factor = getattr(self, 'effectiveness', 1.0)
            if self.random.random() < self.model.generation_rate * effectiveness_factor:
                # Get neighboring nodes
                try:
                    neighbors = list(self.model.G.neighbors(self.pos))
                    if neighbors:
                        # Choose a random neighbor
                        target_node = self.random.choice(neighbors)
                        # Get agents at that node
                        cell_agents = self.model.grid.get_cell_list_contents([target_node])
                        # Expose a user if found
                        for agent in cell_agents:
                            if agent.agent_type == "user" and not agent.exposed:
                                agent.exposed = True
                                print(f"Agent {agent.unique_id} was exposed by generator {self.unique_id}")
                                break
                except Exception as e:
                    print(f"Error in generator step: {e}")
                            
        elif self.agent_type == "detector":
            # Detectors try to identify and neutralize generators or label content
            if self.random.random() < self.model.detection_rate:
                try:
                    # Get neighboring nodes
                    neighbors = list(self.model.G.neighbors(self.pos))
                    if neighbors:
                        # Choose a random neighbor
                        target_node = self.random.choice(neighbors)
                        # Get agents at that node
                        cell_agents = self.model.grid.get_cell_list_contents([target_node])
                        
                        # FIRST PRIORITY: Try to find and neutralize a generator (AI-to-AI interaction)
                        for agent in cell_agents:
                            if agent.agent_type == "generator" and hasattr(agent, 'neutralized') and not agent.neutralized:
                                # Generator may evade detection
                                if self.random.random() > agent.evasion_skill:
                                    # Reduce generator effectiveness - DIRECT AI-TO-AI IMPACT
                                    agent.effectiveness -= 0.2
                                    print(f"Detector {self.unique_id} found and impacted generator {agent.unique_id}! Generator effectiveness reduced to {agent.effectiveness}")
                                    
                                    # Neutralize if effectiveness drops below threshold
                                    if agent.effectiveness <= 0.4:
                                        agent.neutralized = True
                                        self.ai_victories += 1
                                        print(f"Generator {agent.unique_id} has been neutralized by detector {self.unique_id}!")
                                        self.model.record_ai_battle(self.unique_id, agent.unique_id, "detector_win")
                                    else:
                                        self.model.record_ai_battle(self.unique_id, agent.unique_id, "detector_hit")
                                else:
                                    # Generator successfully evaded
                                    print(f"Generator {agent.unique_id} evaded detection by detector {self.unique_id}!")
                                    self.model.record_ai_battle(self.unique_id, agent.unique_id, "generator_evaded")
                                
                                # End turn after AI-to-AI interaction
                                return
                        
                        # SECOND PRIORITY: Label an exposed user if no generator found
                        for agent in cell_agents:
                            if agent.agent_type == "user" and agent.exposed and not agent.labeled:
                                if self.random.random() < self.model.detection_accuracy:
                                    agent.labeled = True
                                    print(f"Agent {agent.unique_id} was labeled by detector {self.unique_id}")
                                    break
                except Exception as e:
                    print(f"Error in detector step: {e}")
                                
        elif self.agent_type == "user":
            # Users can spread content to their neighbors
            if self.exposed and not self.labeled:
                if self.random.random() < self.model.spread_rate:
                    try:
                        # Get neighboring nodes
                        neighbors = list(self.model.G.neighbors(self.pos))
                        if neighbors:
                            # Choose a random neighbor
                            target_node = self.random.choice(neighbors)
                            # Get agents at that node
                            cell_agents = self.model.grid.get_cell_list_contents([target_node])
                            # Expose another user if found
                            for agent in cell_agents:
                                if agent.agent_type == "user" and not agent.exposed:
                                    agent.exposed = True
                                    print(f"Agent {agent.unique_id} was exposed by user {self.unique_id}")
                                    break
                    except Exception as e:
                        print(f"Error in user step: {e}")

class ContentSpreadModel(Model):
    """Model for simulating the spread of deepfake content in a social network."""
    
    def __init__(
        self,
        num_users=30,
        num_generators=3,
        num_detectors=5,
        generation_rate=0.3,
        detection_rate=0.3,
        detection_accuracy=0.8,
        spread_rate=0.4,
        max_steps=100,  # Maximum number of steps before auto-stopping
        auto_stop_when_all_exposed=True  # Whether to stop automatically when all users are exposed
    ):
        super().__init__()
        self.num_users = num_users
        self.num_generators = num_generators
        self.num_detectors = num_detectors
        self.generation_rate = generation_rate
        self.detection_rate = detection_rate
        self.detection_accuracy = detection_accuracy
        self.spread_rate = spread_rate
        self.max_steps = max_steps
        self.auto_stop_when_all_exposed = auto_stop_when_all_exposed
        self.running = True
        
        # Track AI battle outcomes
        self.ai_battles = []
        self.active_generators = num_generators
        self.neutralized_generators = 0
        
        # Create schedule for agent activation
        self.schedule = RandomActivation(self)
        
        # Create social network
        self.G = nx.watts_strogatz_graph(
            n=self.num_users + self.num_generators + self.num_detectors,
            k=4,  # Each node connected to 4 neighbors
            p=0.3  # 30% probability of rewiring each edge
        )
        
        # Create grid from network
        self.grid = NetworkGrid(self.G)
        
        # Create and place agents
        # First, create regular users
        for i in range(self.num_users):
            agent = ContentAgent(i, self, "user")
            self.schedule.add(agent)
            self.grid.place_agent(agent, i)
            agent.pos = i
            
        # Create content generators (RED nodes in visualization)
        for i in range(self.num_generators):
            agent = ContentAgent(self.num_users + i, self, "generator")
            self.schedule.add(agent)
            pos = self.num_users + i
            self.grid.place_agent(agent, pos)
            agent.pos = pos
            
        # Create content detectors (GREEN nodes in visualization)
        for i in range(self.num_detectors):
            agent = ContentAgent(
                self.num_users + self.num_generators + i,
                self,
                "detector"
            )
            self.schedule.add(agent)
            pos = self.num_users + self.num_generators + i
            self.grid.place_agent(agent, pos)
            agent.pos = pos
            
        # Infect a random user to start
        if num_users > 0:
            random_user = self.random.randint(0, num_users - 1)
            agent = self.schedule.agents[random_user]
            agent.exposed = True
            print(f"Starting with agent {agent.unique_id} exposed")
        
        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Unexposed": lambda m: self.count_unexposed(),  # BLUE line in chart
                "Exposed": lambda m: self.count_exposed(),      # RED line in chart
                "Labeled": lambda m: self.count_labeled(),      # GREY line in chart
                "ActiveGenerators": lambda m: self.count_active_generators(),  # Track active generators
                "NeutralizedGenerators": lambda m: self.count_neutralized_generators()  # Track neutralized generators
            }
        )
        
        # Collect initial data
        self.datacollector.collect(self)
        print(f"Model initialized with {self.num_users} users, {self.num_generators} generators, and {self.num_detectors} detectors")
        
    def record_ai_battle(self, detector_id, generator_id, outcome):
        """Record an AI battle outcome for tracking."""
        self.ai_battles.append({
            "step": self.schedule.steps,
            "detector_id": detector_id,
            "generator_id": generator_id,
            "outcome": outcome
        })
        
        # Update active/neutralized generator counts
        if outcome == "detector_win":
            self.active_generators -= 1
            self.neutralized_generators += 1
        
    def step(self):
        """Advance the model by one step."""
        print(f"Step {self.schedule.steps + 1}")
        self.schedule.step()
        self.datacollector.collect(self)
        
        # Print statistics
        unexposed = self.count_unexposed()
        exposed = self.count_exposed()
        labeled = self.count_labeled()
        active_gens = self.count_active_generators()
        neutralized_gens = self.count_neutralized_generators()
        print(f"Unexposed: {unexposed}, Exposed: {exposed}, Labeled: {labeled}")
        print(f"AI Battle Status: {active_gens} active generators, {neutralized_gens} neutralized generators")
        
        # Check stopping conditions
        should_stop = False
        stop_reason = ""
        
        # Stop if maximum steps reached
        if self.schedule.steps >= self.max_steps:
            should_stop = True
            stop_reason = f"Maximum steps ({self.max_steps}) reached."
        
        # Stop if all users are exposed and auto-stop is enabled
        if self.auto_stop_when_all_exposed and unexposed == 0:
            should_stop = True
            stop_reason = "All users have been exposed or labeled."
        
        # Stop if all generators are neutralized
        if active_gens == 0:
            should_stop = True
            stop_reason = "All generator AIs have been neutralized by detector AIs."
        
        if should_stop:
            self.running = False
            print(f"Simulation stopped after {self.schedule.steps} steps.")
            print(stop_reason)
            # Print AI battle summary
            print(f"AI BATTLE SUMMARY: {neutralized_gens}/{self.num_generators} generators neutralized by detectors")
        
    def count_unexposed(self):
        """Count number of unexposed users."""
        return sum(1 for agent in self.schedule.agents 
                  if agent.agent_type == "user" and not agent.exposed)
    
    def count_exposed(self):
        """Count number of exposed but unlabeled users."""
        return sum(1 for agent in self.schedule.agents 
                  if agent.agent_type == "user" and agent.exposed and not agent.labeled)
    
    def count_labeled(self):
        """Count number of users with labeled content."""
        return sum(1 for agent in self.schedule.agents 
                  if agent.agent_type == "user" and agent.labeled)
                  
    def count_active_generators(self):
        """Count number of active generator AIs."""
        return sum(1 for agent in self.schedule.agents 
                  if agent.agent_type == "generator" and not getattr(agent, 'neutralized', False))
    
    def count_neutralized_generators(self):
        """Count number of neutralized generator AIs."""
        return sum(1 for agent in self.schedule.agents 
                  if agent.agent_type == "generator" and getattr(agent, 'neutralized', False))

# Add an alias for the model class that matches what run.py is trying to import
DeepfakeModel = ContentSpreadModel 