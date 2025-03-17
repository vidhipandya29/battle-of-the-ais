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
        
    def step(self):
        """Agent's behavior during each step of the simulation."""
        # Skip if position is not set
        if self.pos is None:
            return
            
        if self.agent_type == "generator":
            # Generators create and spread deepfake content
            if self.random.random() < self.model.generation_rate:
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
            # Detectors try to identify and label deepfake content
            if self.random.random() < self.model.detection_rate:
                try:
                    # Get neighboring nodes
                    neighbors = list(self.model.G.neighbors(self.pos))
                    if neighbors:
                        # Choose a random neighbor
                        target_node = self.random.choice(neighbors)
                        # Get agents at that node
                        cell_agents = self.model.grid.get_cell_list_contents([target_node])
                        # Label an exposed user if found
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
                "Labeled": lambda m: self.count_labeled()       # GREY line in chart
            }
        )
        
        # Collect initial data
        self.datacollector.collect(self)
        print(f"Model initialized with {self.num_users} users, {self.num_generators} generators, and {self.num_detectors} detectors")
        
    def step(self):
        """Advance the model by one step."""
        print(f"Step {self.schedule.steps + 1}")
        self.schedule.step()
        self.datacollector.collect(self)
        
        # Print statistics
        unexposed = self.count_unexposed()
        exposed = self.count_exposed()
        labeled = self.count_labeled()
        print(f"Unexposed: {unexposed}, Exposed: {exposed}, Labeled: {labeled}")
        
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
        
        if should_stop:
            self.running = False
            print(f"Simulation stopped after {self.schedule.steps} steps.")
            print(stop_reason)
        
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