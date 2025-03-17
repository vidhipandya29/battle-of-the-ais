from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule, TextElement
from mesa.visualization.UserParam import Slider, Checkbox

# Create a legend element to explain the node colors
class LegendElement(TextElement):
    def __init__(self):
        pass
        
    def render(self, model):
        return """
        <div style="background-color: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin-bottom: 15px;">
            <h3 style="margin-top: 0;">Node Color Legend:</h3>
            <ul style="margin-bottom: 0;">
                <li><span style="color: blue; font-weight: bold;">Blue:</span> Unexposed Users - users who haven't encountered deepfake content</li>
                <li><span style="color: red; font-weight: bold;">Red:</span> Content Generators and Exposed Users - sources of deepfake content or users who have encountered it</li>
                <li><span style="color: green; font-weight: bold;">Green:</span> Content Detectors - AI systems that identify and label deepfake content</li>
                <li><span style="color: grey; font-weight: bold;">Grey:</span> Labeled Users - users who have encountered deepfake content that has been identified and labeled</li>
            </ul>
        </div>
        """

def network_portrayal(G):
    """Draw the network of agents and their states."""
    # Initialize empty portrayal
    portrayal = dict()
    
    # Add nodes
    portrayal["nodes"] = []
    for node_id in G.nodes():
        # Get agents at this node
        agents = G.nodes[node_id].get("agent", [])
        if not agents:
            continue
            
        # Get the first agent
        agent = agents[0]
        
        # Determine color based on agent state
        color = "blue"  # Default for unexposed users - matches BLUE line in chart
        size = 5       # Default size for regular users
        
        # Special colors for different agent types and states
        if agent.agent_type == "generator":
            color = "red"     # Content generators are RED
            size = 8          # Larger size for special agents
        elif agent.agent_type == "detector":
            color = "green"   # Content detectors are GREEN (not tracked in chart)
            size = 8          # Larger size for special agents
        elif agent.exposed:
            if agent.labeled:
                color = "grey"  # Labeled users are GREY - matches GREY line in chart
            else:
                color = "red"   # Exposed users are RED - matches RED line in chart
        
        # Add node to portrayal
        portrayal["nodes"].append({
            "id": node_id,
            "size": size,
            "color": color,
            "label": agent.agent_type
        })
    
    # Add edges
    portrayal["edges"] = []
    for source, target in G.edges():
        portrayal["edges"].append({
            "source": source,
            "target": target,
            "color": "black",
            "width": 1
        })
    
    return portrayal

def create_model_visualization(model_class):
    """Create a visualization server for the model."""
    # Create legend
    legend = LegendElement()
    
    # Network visualization
    network = NetworkModule(network_portrayal, 500, 500)
    
    # Chart for data - color coding matches nodes
    chart = ChartModule([
        {"Label": "Unexposed", "Color": "blue"},  # BLUE: unexposed users
        {"Label": "Exposed", "Color": "red"},     # RED: exposed users
        {"Label": "Labeled", "Color": "grey"}     # GREY: labeled users
    ])
    
    # Model parameters
    model_params = {
        "num_users": Slider(
            "Number of Users", 
            value=30,
            min_value=10, 
            max_value=100, 
            step=10,
            description="Number of regular users"
        ),
        "num_generators": Slider(
            "Number of Generators", 
            value=3, 
            min_value=1, 
            max_value=10, 
            step=1,
            description="Number of content generators (RED nodes)"
        ),
        "num_detectors": Slider(
            "Number of Detectors", 
            value=5, 
            min_value=1, 
            max_value=15, 
            step=1,
            description="Number of content detectors (GREEN nodes)"
        ),
        "generation_rate": Slider(
            "Generation Rate", 
            value=0.3, 
            min_value=0.01, 
            max_value=1.0, 
            step=0.01,
            description="Rate of content generation"
        ),
        "detection_rate": Slider(
            "Detection Rate", 
            value=0.3, 
            min_value=0.01, 
            max_value=1.0, 
            step=0.01,
            description="Rate of content detection"
        ),
        "detection_accuracy": Slider(
            "Detection Accuracy", 
            value=0.8, 
            min_value=0.5, 
            max_value=1.0, 
            step=0.05,
            description="Accuracy of detection"
        ),
        "spread_rate": Slider(
            "Spread Rate", 
            value=0.4, 
            min_value=0.01, 
            max_value=1.0, 
            step=0.01,
            description="Rate of content spread"
        ),
        "max_steps": Slider(
            "Maximum Steps", 
            value=100, 
            min_value=10, 
            max_value=500, 
            step=10,
            description="Maximum simulation steps before auto-stopping"
        ),
        "auto_stop_when_all_exposed": Checkbox(
            "Auto-Stop When All Exposed", 
            value=True,
            description="Stop the simulation automatically when all users have been exposed"
        )
    }
    
    # Create and return server
    server = ModularServer(
        model_class,
        [legend, network, chart],  # Added legend as the first element
        "Battle of the AIs: Deepfake Content Spread Model",
        model_params
    )
    
    return server 