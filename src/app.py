import math
import solara
from mesa.examples.basic.virus_on_network.model import (
    State,
    VirusOnNetwork,
    number_infected
)
from mesa.visualization import (
    SolaraViz,
    make_plot_component,
    make_space_component,
)


def agent_portrayal(agent):
    node_color_dict = {
        State.INFECTED: "tab:red",
        State.SUSCEPTIBLE: "tab:green",
        State.RESISTANT: "tab:gray",
    }
    return {"color": node_color_dict[agent.state], "size": 10}


def get_resistant_susceptible_ratio(model):
    ratio = model.resistant_susceptible_ratio()
    ratio_text = r"$\infty$" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(number_infected(model))

    return solara.Markdown(
        f"Resistant/Susceptible Ratio: {ratio_text}<br>Infected Remaining: {infected_text}"
    )


# Fixed parameters
model_params = {
    "num_nodes": {
        "type": "SliderInt",
        "value": 100,
        "min": 50,
        "max": 500,
        "step": 10,
        "label": "Number of Nodes",
    },
    "avg_node_degree": {
        "type": "SliderInt",
        "value": 3,
        "min": 1,
        "max": 10,
        "step": 1,
        "label": "Average Node Degree",
    },
    "initial_outbreak_size": {
        "type": "SliderInt",
        "value": 1,
        "min": 1,
        "max": 50,
        "step": 1,
        "label": "Initial Outbreak Size",
    },
    "virus_spread_chance": {
        "type": "SliderFloat",
        "value": 0.37,
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
        "label": "Virus Spread Chance",
    },
    "virus_check_frequency": {
        "type": "SliderFloat",
        "value": 0.5,
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
        "label": "AI Detection Frequency",
    },
    "recovery_chance": {
        "type": "SliderFloat",
        "value": 0.3,
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
        "label": "Recovery Chance",
    },
    "gain_resistance_chance": {
        "type": "SliderFloat",
        "value": 0.5,
        "min": 0.01,
        "max": 1.0,
        "step": 0.01,
        "label": "Resistance Gain Chance",
    },
}


def post_process_lineplot(ax):
    ax.set_ylim(ymin=0)
    ax.set_ylabel("# of users")

    new_labels = [
        "Interacted with AI Content",
        "Viewed AI Content",
        "Viewed labelled AI content",
    ]

    currentlegend = ax.get_legend()
    if currentlegend:
        for text, label in zip(currentlegend.get_texts(), new_labels):
            text.set_text(label)


SpacePlot = make_space_component(agent_portrayal)
StatePlot = make_plot_component(
    {"Infected": "tab:red", "Susceptible": "tab:green", "Resistant": "tab:gray"},
    post_process=post_process_lineplot,
)

# Initialize the model with the fixed parameters
model1 = VirusOnNetwork()

page = SolaraViz(
    model1,
    components=[
        SpacePlot,
        StatePlot,
        get_resistant_susceptible_ratio,
    ],
    model_params=model_params, 
    name="Battle of the AIs",
)
page  # noqa
