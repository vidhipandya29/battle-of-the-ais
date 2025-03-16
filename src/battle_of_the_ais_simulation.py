from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import NetworkModule, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
import socket
import threading
import time

class FixedNetworkModule(NetworkModule):
    """Custom NetworkModule to ensure the full DeepfakeModel is passed."""

    def render(self, model):
        """Override render to ensure the full model is passed to the portrayal function."""
        if isinstance(model, nx.Graph):  # Check if we got model.G instead of full model
            print("🚨 ERROR: render() received model.G instead of full model! Forcing correction...")
            return {"nodes": [], "edges": []}

        return self.portrayal_method(model)  # Ensure full model is passed

class SocialMediaAgent(Agent):
    """Base class for all agents in the simulation."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.engagement_level = 0  # Tracks likes, shares, comments

class UserAgent(SocialMediaAgent):
    """Represents a social media user interacting with AI-generated content."""
    def __init__(self, unique_id, model, role):
        super().__init__(unique_id, model)
        self.role = role  # 'regular', 'influential', 'skeptical', 'trusting'
        self.exposed = False  # Has the user seen deepfake content?
        self.engaged = False  # Has the user engaged with deepfake content?
        self.awareness = False  # Is the user aware content is AI-generated?
    
    def step(self):
        # Get neighbors in the network
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        
        # Check if any deepfake content has been labeled
        labeled_content = any(
            isinstance(agent, DeepfakeContent) and agent.labeled 
            for node in neighbors 
            for agent in self.model.grid.get_cell_list_contents([node])
        )
        
        # Process each neighbor
        for node in neighbors:
            agents = self.model.grid.get_cell_list_contents([node])
            for agent in agents:
                # If neighbor is deepfake content
                if isinstance(agent, DeepfakeContent):
                    # Mark user as exposed
                    self.exposed = True
                    
                    # Engagement logic based on user role and content labeling
                    engagement_probability = self.calculate_engagement_probability(agent)
                    
                    if self.random.random() < engagement_probability:
                        self.engaged = True
                        agent.engagement_count += 1
                        
                        # Virality boost based on role
                        if self.role == 'influential' and self.random.random() < 0.4:
                            agent.viral = True
                            print(f"🔥 Agent {self.unique_id} ({self.role}) made content {agent.unique_id} go viral!")
                            
    def calculate_engagement_probability(self, content):
        """Calculate probability of engaging with content based on role and labeling."""
        base_prob = {
            'regular': 0.5,    # Average engagement
            'influential': 0.7, # Higher engagement
            'skeptical': 0.3,   # Lower engagement
            'trusting': 0.8     # Very high engagement
        }.get(self.role, 0.5)
        
        # Adjust based on content labeling
        if content.labeled:
            # Labeled content: different roles respond differently to labels
            if self.role == 'skeptical':
                return base_prob * 0.2  # Skeptical users avoid labeled content
            elif self.role == 'trusting':
                return base_prob * 0.5  # Trusting users reduce engagement with labeled content
            else:
                return base_prob * 0.7  # Regular/influential users somewhat reduce engagement
        else:
            # Unlabeled content
            return base_prob

class DeepfakeContent(SocialMediaAgent):
    """Represents AI-generated deepfake content in the social network."""
    def __init__(self, unique_id, model, creator_id):
        super().__init__(unique_id, model)
        self.creator_id = creator_id  # ID of the DeepfakeGenerator that created this
        self.created_time = model.schedule.steps  # When the content was created
        self.labeled = False  # Has it been labeled as AI-generated?
        self.true_label = True  # It is indeed an AI-generated deepfake
        self.engagement_count = 0  # Number of users who engaged
        self.viral = False  # Has the content gone viral?
        
        # Content properties
        self.quality = self.random.uniform(0.3, 1.0)  # How convincing/high-quality is the deepfake
        self.controversial = self.random.random() < 0.3  # Is the content controversial?
    
    def step(self):
        # Content doesn't take actions by itself
        pass

class DeepfakeGenerator(SocialMediaAgent):
    """AI bot that creates and distributes deepfake content."""
    def __init__(self, unique_id, model, sophistication):
        super().__init__(unique_id, model)
        self.sophistication = sophistication  # 0.0-1.0, how advanced the generator is
        self.content_created = 0
        
    def step(self):
        # Create new deepfake content with a certain probability
        if self.random.random() < 0.1:  # 10% chance to create content each step
            # Create deepfake content
            content_id = f"content_{self.unique_id}_{self.model.next_content_id}"
            self.model.next_content_id += 1
            
            # Create the content agent
            content = DeepfakeContent(content_id, self.model, self.unique_id)
            self.model.schedule.add(content)
            
            # Place in a random node to start spreading
            available_nodes = list(self.model.G.nodes())
            selected_node = self.random.choice(available_nodes)
            self.model.grid.place_agent(content, selected_node)
            
            self.content_created += 1
            print(f"🤖 Generator {self.unique_id} created content {content_id} at node {selected_node}")

class ContentDetector(SocialMediaAgent):
    """AI system that detects and labels AI-generated content."""
    def __init__(self, unique_id, model, accuracy, response_time):
        super().__init__(unique_id, model)
        self.accuracy = accuracy  # 0.0-1.0, detection accuracy
        self.response_time = response_time  # Steps needed to detect content
        self.detection_queue = {}  # {content_id: steps_remaining}
        self.content_reviewed = 0
        self.true_positives = 0
        self.false_positives = 0
        
    def step(self):
        # Look for new unlabeled content to review
        all_content = [
            agent for agent in self.model.schedule.agents 
            if isinstance(agent, DeepfakeContent) and not agent.labeled
        ]
        
        # Add new content to detection queue
        for content in all_content:
            if content.unique_id not in self.detection_queue:
                # More viral content gets detected faster
                priority_factor = 0.5 if content.viral else 1.0
                detection_time = max(1, int(self.response_time * priority_factor))
                self.detection_queue[content.unique_id] = detection_time
                print(f"🔍 Detector {self.unique_id} queued content {content.unique_id} for review")
        
        # Process items in the queue
        completed = []
        for content_id, time_left in self.detection_queue.items():
            self.detection_queue[content_id] = time_left - 1
            
            # Detection complete
            if self.detection_queue[content_id] <= 0:
                completed.append(content_id)
                
        # Apply detection results
        for content_id in completed:
            content_agents = [
                agent for agent in self.model.schedule.agents 
                if isinstance(agent, DeepfakeContent) and agent.unique_id == content_id
            ]
            
            if content_agents:
                content = content_agents[0]
                self.content_reviewed += 1
                
                # Determine if detection is accurate based on detector accuracy
                detection_successful = self.random.random() < self.accuracy
                
                if detection_successful:
                    content.labeled = True
                    self.true_positives += 1
                    print(f"✅ Detector {self.unique_id} correctly labeled {content_id} as deepfake")
                else:
                    self.false_positives += 1
                    print(f"❌ Detector {self.unique_id} failed to detect {content_id}")
            
            # Remove from queue
            del self.detection_queue[content_id]

class DeepfakeModel(Model):
    """Model simulating the spread of deepfake content and detection efforts."""
    def __init__(self, num_users=100, num_generators=2, num_detectors=5, 
                 network_type='small_world', detection_accuracy=0.85, 
                 response_time=3, num_steps=50):
        self.num_users = num_users
        self.num_generators = num_generators
        self.num_detectors = num_detectors
        self.schedule = RandomActivation(self)
        self.detection_accuracy = detection_accuracy
        self.response_time = response_time
        self.num_steps = num_steps
        self.next_content_id = 0
        self.running = True
        
        # Create network structure
        if network_type == 'small_world':
            self.G = nx.watts_strogatz_graph(num_users, k=6, p=0.3)
        elif network_type == 'scale_free':
            self.G = nx.barabasi_albert_graph(num_users, m=3)
        else:
            self.G = nx.erdos_renyi_graph(num_users, p=0.05)
        
        self.grid = NetworkGrid(self.G)
        
        # Create user agents
        for i in range(num_users):
            role = np.random.choice(
                ['regular', 'influential', 'skeptical', 'trusting'], 
                p=[0.6, 0.1, 0.15, 0.15]
            )
            agent = UserAgent(i, self, role)
            self.schedule.add(agent)
            self.grid.place_agent(agent, i)
        
        # Create generator agents (AI bots creating deepfakes)
        for i in range(num_generators):
            generator_id = f"generator_{i}"
            sophistication = self.random.uniform(0.5, 0.9)
            generator = DeepfakeGenerator(generator_id, self, sophistication)
            self.schedule.add(generator)
            # Generators don't need network positions
            
        # Create detector agents (AI systems detecting deepfakes)
        for i in range(num_detectors):
            detector_id = f"detector_{i}"
            # Vary accuracy and response time
            accuracy = self.random.uniform(
                self.detection_accuracy - 0.1, 
                self.detection_accuracy + 0.1
            )
            resp_time = max(1, int(self.random.normalvariate(
                self.response_time, 
                self.response_time * 0.3
            )))
            detector = ContentDetector(detector_id, self, accuracy, resp_time)
            self.schedule.add(detector)
            # Detectors don't need network positions
        
        # Set up data collection
        self.datacollector = DataCollector({
            "Exposed": lambda m: sum(1 for a in m.schedule.agents 
                                     if isinstance(a, UserAgent) and a.exposed),
            "Engaged": lambda m: sum(1 for a in m.schedule.agents 
                                     if isinstance(a, UserAgent) and a.engaged),
            "ContentCreated": lambda m: sum(1 for a in m.schedule.agents 
                                           if isinstance(a, DeepfakeContent)),
            "ContentLabeled": lambda m: sum(1 for a in m.schedule.agents 
                                           if isinstance(a, DeepfakeContent) and a.labeled),
            "ViralContent": lambda m: sum(1 for a in m.schedule.agents 
                                         if isinstance(a, DeepfakeContent) and a.viral),
        })

    def step(self):
        """Run one step of the simulation."""
        self.schedule.step()
        self.datacollector.collect(self)
        
        # Calculate metrics for reporting
        total_content = sum(1 for a in self.schedule.agents if isinstance(a, DeepfakeContent))
        labeled_content = sum(1 for a in self.schedule.agents 
                             if isinstance(a, DeepfakeContent) and a.labeled)
        exposed_users = sum(1 for a in self.schedule.agents 
                           if isinstance(a, UserAgent) and a.exposed)
        engaged_users = sum(1 for a in self.schedule.agents 
                           if isinstance(a, UserAgent) and a.engaged)
        
        print(f"Step: {self.schedule.steps} | Content: {total_content} | Labeled: {labeled_content} | " +
              f"Exposed Users: {exposed_users}/{self.num_users} | " +
              f"Engaged Users: {engaged_users}/{self.num_users}")
        
        # Optional: Stop after max steps or other condition
        if self.schedule.steps >= self.num_steps:
            self.running = False

# Find an available port dynamically
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

server_port = find_free_port()

# Interactive visualization setup
def network_portrayal(model):
    """Define how agents and network appear in visualization."""
    portrayal = {
        "nodes": [],
        "edges": [{"id": f"{s}-{t}", "source": s, "target": t, "color": "black", "width": 1} 
                 for s, t in model.G.edges()]
    }

    for node in model.G.nodes():
        agents = model.grid.get_cell_list_contents([node])
        if not agents:
            continue
            
        # Handle multiple agents in same node
        user_agents = [a for a in agents if isinstance(a, UserAgent)]
        content_agents = [a for a in agents if isinstance(a, DeepfakeContent)]
        
        # Prioritize content visualization if present
        if content_agents:
            content = content_agents[0]
            if content.labeled:
                color = "red"  # Labeled deepfake content
                size = 10
            elif content.viral:
                color = "orange"  # Viral unlabeled content
                size = 15
            else:
                color = "green"  # Regular unlabeled content
                size = 8
                
            portrayal["nodes"].append({
                "id": node,
                "color": color,
                "size": size,
                "shape": "rect"  # Square for content
            })
        elif user_agents:
            user = user_agents[0]
            
            # Coloring for user agents
            if user_agents:
                user = user_agents[0]
                
                # Color based on user status and role
                if user.engaged:
                    color = "purple"  # User engaged with deepfake
                elif user.exposed:
                    color = "yellow"  # User exposed but not engaged
                else:
                    # Role-based coloring for unexposed users
                    color = {
                        "regular": "gray",
                        "influential": "blue",
                        "skeptical": "pink",
                        "trusting": "cyan"
                    }.get(user.role, "white")
                
                size = 8 if user.role == "influential" else 6
                
                portrayal["nodes"].append({
                    "id": node,
                    "color": color,
                    "size": size,
                    "label": user.role[0].upper()  # First letter of role
                })
    
    return portrayal

class LegendElement(TextElement):
    """Legend explaining the visualization elements."""
    def render(self, model):
        return """
        <b>User Legend:</b> 
        <span style="color:gray">⬤</span> Regular User | 
        <span style="color:blue">⬤</span> Influential | 
        <span style="color:pink">⬤</span> Skeptical | 
        <span style="color:cyan">⬤</span> Trusting | 
        <span style="color:yellow">⬤</span> Exposed | 
        <span style="color:purple">⬤</span> Engaged<br>
        <b>Content Legend:</b> 
        <span style="color:green">■</span> Unlabeled Content | 
        <span style="color:orange">■</span> Viral Content | 
        <span style="color:red">■</span> Labeled Content
        """

class StatsElement(TextElement):
    """Display real-time statistics in the UI."""
    def render(self, model):
        total_content = sum(1 for a in model.schedule.agents if isinstance(a, DeepfakeContent))
        labeled_content = sum(1 for a in model.schedule.agents 
                          if isinstance(a, DeepfakeContent) and a.labeled)
        
        # Calculate detector metrics
        detectors = [a for a in model.schedule.agents if isinstance(a, ContentDetector)]
        total_reviewed = sum(d.content_reviewed for d in detectors)
        true_positives = sum(d.true_positives for d in detectors)
        false_positives = sum(d.false_positives for d in detectors)
        
        # Calculate detection accuracy if any content has been reviewed
        accuracy = (true_positives / total_reviewed * 100) if total_reviewed > 0 else 0
        
        # AI-to-AI metrics
        ai_generator_count = sum(1 for a in model.schedule.agents if isinstance(a, DeepfakeGenerator))
        ai_detector_count = sum(1 for a in model.schedule.agents if isinstance(a, ContentDetector))
        
        return f"""
        <b>Users:</b> Exposed: {sum(1 for a in model.schedule.agents if isinstance(a, UserAgent) and a.exposed)} / 
        Engaged: {sum(1 for a in model.schedule.agents if isinstance(a, UserAgent) and a.engaged)}<br>
        <b>Content:</b> Total: {total_content} / 
        Labeled: {labeled_content} ({int(labeled_content/total_content*100) if total_content else 0}%) /
        Viral: {sum(1 for a in model.schedule.agents if isinstance(a, DeepfakeContent) and a.viral)}<br>
        <b>AI Systems:</b> Generators: {ai_generator_count} / 
        Detectors: {ai_detector_count} / 
        Detection Accuracy: {accuracy:.1f}%
        """

class ChartLabels(TextElement):
    """Axis labels for the chart."""
    def render(self, model):
        return """
        <div style="position: relative; display: flex; align-items: center; justify-content: center;">
            <!-- Y-axis label -->
            <div style="position: absolute; left: -140px; top: -500%; transform: rotate(-90deg) translateY(-50%); font-size: 14px;">
                Number of Users & Content
            </div>
            
            <div style="text-align: center; margin-top: 10px; font-size: 14px; font-weight;">
                Simulation Steps
            </div>
        </div>
        """

# Set up visualization elements
chart_labels = ChartLabels()
network_vis = FixedNetworkModule(network_portrayal, 500, 500)
chart = ChartModule([
    {"Label": "Exposed", "Color": "yellow"}, 
    {"Label": "Engaged", "Color": "purple"},
    {"Label": "ContentCreated", "Color": "green"}, 
    {"Label": "ContentLabeled", "Color": "red"},
    {"Label": "ViralContent", "Color": "orange"}
])
stats = StatsElement()
legend = LegendElement()

server = ModularServer(
    DeepfakeModel, 
    [network_vis, chart, chart_labels, stats, legend], 
    "Deepfake Content Detection Simulation",
    {
        "num_users": 100,
        "num_generators": 2,  
        "num_detectors": 5,   
        "network_type": "small_world",
        "detection_accuracy": 0.85,
        "response_time": 3,
        "num_steps": 50
    }
)

server.port = server_port

# Run both the interactive UI and batch simulations
if __name__ == "__main__":
    # Start the Mesa UI in a separate thread
    def run_mesa_ui():
        print(f"Launching Mesa interactive UI at http://127.0.0.1:{server_port}...")
        server.launch(open_browser=True)
    
    ui_thread = threading.Thread(target=run_mesa_ui)
    ui_thread.start()
    
    print("Running batch simulations and generating visualizations...")
    num_runs = 10
    all_data = []
    
    # Parameter combinations to test
    accuracy_levels = [0.7, 0.8, 0.9]
    response_times = [2, 4, 6]
    network_types = ["small_world", "scale_free"]
    
    results = []
    
    # Run parameter sweep
    for accuracy in accuracy_levels:
        for response_time in response_times:
            for network in network_types:
                print(f"\nTesting parameters: accuracy={accuracy}, response_time={response_time}, network={network}")
                
                # Run with these parameters
                model = DeepfakeModel(
                    num_users=100,
                    num_generators=2,
                    num_detectors=5,
                    network_type=network,
                    detection_accuracy=accuracy,
                    response_time=response_time,
                    num_steps=40
                )
                
                # Run simulation
                for i in range(model.num_steps):
                    model.step()
                
                # Collect final state data
                data = model.datacollector.get_model_vars_dataframe()
                
                # Calculate metrics
                final_step_data = data.iloc[-1]
                total_users = model.num_users
                total_content = final_step_data["ContentCreated"]
                labeled_content = final_step_data["ContentLabeled"]
                exposed_users = final_step_data["Exposed"]
                engaged_users = final_step_data["Engaged"]
                
                # Calculate derived metrics
                labeling_rate = labeled_content / total_content if total_content > 0 else 0
                exposure_rate = exposed_users / total_users
                engagement_rate = engaged_users / exposed_users if exposed_users > 0 else 0
                
                # Store results
                results.append({
                    "accuracy": accuracy,
                    "response_time": response_time,
                    "network_type": network,
                    "total_content": total_content,
                    "labeled_content": labeled_content,
                    "labeling_rate": labeling_rate,
                    "exposed_users": exposed_users,
                    "exposure_rate": exposure_rate,
                    "engaged_users": engaged_users, 
                    "engagement_rate": engagement_rate,
                })
                
                # Store full time series data
                data["accuracy"] = accuracy
                data["response_time"] = response_time
                data["network_type"] = network
                all_data.append(data)
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results)
    results_df.to_csv("deepfake_simulation_results.csv", index=False)
    print(f"Saved results to deepfake_simulation_results.csv")
    
    # Combine all time series data
    all_runs_df = pd.concat(all_data)
    all_runs_df.to_csv("deepfake_simulation_timeseries.csv", index=False)
    
    # Create summary visualizations
    plt.figure(figsize=(10, 6))
    # First create a filtered dataframe
    small_world_df = all_runs_df[all_runs_df["network_type"] == "small_world"]
    # Then use that filtered dataframe for the plot and its own index
    sns.lineplot(
        data=small_world_df, 
        x=small_world_df.index, 
        y="Engaged",
        hue="accuracy",
        style="response_time",
        markers=True,
        dashes=False
    )
    plt.title("User Engagement Over Time by Detection Parameters (Small World Network)")
    plt.xlabel("Simulation Steps")
    plt.ylabel("Number of Engaged Users")
    plt.savefig("engagement_by_detection_params.png")
    
    # Create AI vs AI effectiveness visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=results_df,
        x="labeling_rate", 
        y="engagement_rate",
        hue="network_type",
        size="response_time",
        style="accuracy"
    )
    plt.title("AI Detection vs. Deepfake Engagement Effectiveness")
    plt.xlabel("Content Labeling Rate")
    plt.ylabel("User Engagement Rate")
    plt.savefig("ai_vs_ai_effectiveness.png")
    
    print("Analysis complete! Check the CSV files and PNG images for results.")