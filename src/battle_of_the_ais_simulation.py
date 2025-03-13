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
from sklearn.metrics import precision_recall_fscore_support
import socket
import threading

class FixedNetworkModule(NetworkModule):
    """Custom NetworkModule to ensure the full MisinformationModel is passed."""

    def render(self, model):
        """Override render to ensure the full model is passed to the portrayal function."""
        if isinstance(model, nx.Graph):  # Check if we got model.G instead of full model
            print("🚨 ERROR: render() received model.G instead of full model! Forcing correction...")
            return {"nodes": [], "edges": []}

        return self.portrayal_method(model)  # Ensure full model is passed

class UserAgent(Agent):
    """Represents a social media user interacting with AI-generated content."""
    def __init__(self, unique_id, model, role):
        super().__init__(unique_id, model)
        self.role = role  # 'susceptible', 'spreader', 'fact_checker', 'influencer', 'skeptical'
        self.infected = False  # Has the user engaged with misinformation?
        self.labeled = False  # Was the content labeled as AI-generated?

    def step(self):
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        for node in neighbors:
            agents = self.model.grid.get_cell_list_contents([node])
            for agent in agents:
                if isinstance(agent, UserAgent):
                    if self.role == 'spreader' and self.random.random() < 0.6:
                        agent.infected = True
                    elif self.role == 'fact_checker' and agent.infected and self.random.random() < 0.7:  
                        agent.labeled = True  
                        print(f"Agent {agent.unique_id} labeled CONTENT!")  # Debugging
                    elif self.role == 'influencer' and self.random.random() < 0.9:  
                        agent.infected = True  
                    elif self.role == 'skeptical' and agent.labeled and self.random.random() < 0.3:  
                        agent.infected = True 


class MisinformationModel(Model):
    def __init__(self, num_agents=100, network_type='small_world', detection_accuracy=0.9, num_steps=50):
        self.num_agents = num_agents
        self.schedule = RandomActivation(self)
        self.detection_accuracy = detection_accuracy
        self.num_steps = num_steps
        self.running = True  # 🚀 This flag controls if the model should keep running
        
        # Create network structure
        if network_type == 'small_world':
            self.G = nx.watts_strogatz_graph(num_agents, k=4, p=0.3)
        else:
            self.G = nx.erdos_renyi_graph(num_agents, p=0.05)
        
        self.grid = NetworkGrid(self.G)
        
        # Assign agents to the network
        for i, node in enumerate(self.G.nodes()):
            role = np.random.choice(
                ['susceptible', 'spreader', 'fact_checker', 'influencer', 'skeptical'], 
                p=[0.3, 0.3, 0.1, 0.2, 0.1]
            )
            agent = UserAgent(i, self, role)
            self.schedule.add(agent)
            self.grid.place_agent(agent, node)

        self.datacollector = DataCollector({
            "Infected": lambda m: sum(a.infected for a in m.schedule.agents),
            "Labeled": lambda m: sum(a.labeled for a in m.schedule.agents),
        })

    def step(self):
        """Run one step and stop when no more changes occur."""
        prev_infected = sum(a.infected for a in self.schedule.agents)
        prev_labeled = sum(a.labeled for a in self.schedule.agents)

        self.schedule.step()
        self.datacollector.collect(self)

        current_infected = sum(a.infected for a in self.schedule.agents)
        current_labeled = sum(a.labeled for a in self.schedule.agents)

        print(f"Step: {self.schedule.steps} | Infected: {current_infected}/{self.num_agents} | Labeled: {current_labeled}/{self.num_agents}")

        # ✅ Stop if there are NO CHANGES in infection or labeling
        if current_infected == prev_infected and current_labeled == prev_labeled:
            print("🚨 No more changes detected. Simulation Stopping.")
            self.running = False  # 🛑 Stop the simulation

# Find an available port dynamically
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

server_port = find_free_port()

# Interactive Mesa Visualization Setup
def network_portrayal(model):
    """Define how agents and edges appear in the network visualization."""
    portrayal = {
        "nodes": [],
        "edges": [{"id": f"{s}-{t}", "source": s, "target": t, "color": "black"} for s, t in model.G.edges()]
    }

    for node in model.G.nodes():
        agents = model.grid.get_cell_list_contents([node])
        if agents:
            agent = agents[0]

            # ✅ Blue (Labeled) takes priority over Red (Infected)
            if agent.labeled:
                color = "blue"  # ✅ Fact-checked content turns blue
            elif agent.infected:
                color = "red"  # 🔴 Misinformation spread
            else:
                role_colors = {
                    "susceptible": "gray",
                    "spreader": "red",
                    "fact_checker": "blue",
                    "influencer": "orange",
                    "skeptical": "purple"
                }
                color = role_colors.get(agent.role, "gray")

            portrayal["nodes"].append({
                "id": node,
                "color": color,
                "size": 10
            })

    return portrayal


class LegendElement(TextElement):
    """Static legend explaining the color representation."""
    def render(self, model):
        return "<b>Legend:</b> " \
               "🔴 Spreader | 🔵 Fact Checker | 🟠 Influencer | 🟣 Skeptical | ⚫ Susceptible"

class StatsElement(TextElement):
    """Display real-time statistics in the UI."""
    def render(self, model):
        return f"<b>Infected Users:</b> {sum([1 for a in model.schedule.agents if a.infected])} / {model.num_agents} " \
               f"<b>| Labeled Content:</b> {sum([1 for a in model.schedule.agents if a.labeled])}"

network_vis = FixedNetworkModule(network_portrayal, 500, 500)

chart = ChartModule([{ "Label": "Infected", "Color": "Red" }, { "Label": "Labeled", "Color": "Blue" }])
stats = StatsElement()
legend = LegendElement()
server = ModularServer(MisinformationModel, [network_vis, chart, stats, legend], "Misinformation Spread Model")
server.port = server_port  # Assigns a free port dynamically

# Run both the interactive UI and the static visualization
if __name__ == "__main__":
    # Start the Mesa UI in a separate thread
    def run_mesa_ui():
        print(f"Launching Mesa interactive UI at http://127.0.0.1:{server_port}...")
        server.launch(open_browser=True)
    
    ui_thread = threading.Thread(target=run_mesa_ui)
    ui_thread.start()
    
    print("Running simulation and generating visualizations...")
    num_runs = 10
    all_data = []
    precision_scores, recall_scores, f1_scores = [], [], []
    
    for run in range(num_runs):
        model = MisinformationModel()
        for i in range(model.num_steps):
            model.step()
        data = model.datacollector.get_model_vars_dataframe()
        data['Run'] = run
        all_data.append(data)
    
        # Compute Precision-Recall for Fact-checking effectiveness
        y_true = [1 if a.infected else 0 for a in model.schedule.agents]
        y_pred = [1 if a.labeled else 0 for a in model.schedule.agents]
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=1)
        precision_scores.append(precision)
        recall_scores.append(recall)
        f1_scores.append(f1)
    
    df_all = pd.concat(all_data)
    df_all.to_csv("misinformation_simulation_results.csv", index=False)
    
    print(f"Average Precision: {np.mean(precision_scores):.2f}")
    print(f"Average Recall: {np.mean(recall_scores):.2f}")
    print(f"Average F1-score: {np.mean(f1_scores):.2f}")
    