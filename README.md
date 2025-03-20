# Battle of the AIs: Deepfake Content Spread Simulation

This project simulates the spread of AI-generated content (deepfakes) in a social network, along with the dynamics between content generators and detectors. It's implemented using the Mesa agent-based modeling framework and adapted from Mesa's virus spread example.

## Features

- Simulates a social network with agents in different states:
  - Susceptible: Users who have viewed but not interacted with AI content (green line in chart)
  - Infected: Users who have interacted with AI content (red line in chart)
  - Resistant: Users who have viewed labeled AI content (gray line in chart)
- Interactive visualization showing the network structure and agent states
- Real-time charts tracking the spread of content
- Visualization of the simulation over time with step controls

## Running the Simulation
1. Make sure you have Python 3.8 or higher installed

2. Clone the repository.
    ```bash
    git clone https://github.com/vidhipandya29 battle-of-the-ais.git
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Navigate to the src directory:
    ```bash
    cd src
    ```

5. Run the server:
    ```bash
    solara run app.py
    ```

6. Open your web browser and go to:
    ```
    http://localhost:8765
    ```

## Controls

The simulation interface includes:
- Play Interval (ms): Control simulation speed
- Render Interval (steps): Control visualization update frequency
- Reset: Reset the simulation to initial state
- Play/Pause: Start or pause the simulation
- Step: Advance the simulation by one step

## Visualization

The visualization includes:
- Network view showing agents and their connections
- Color coding:
  - Green: Susceptible users (viewed but not interacted with AI content)
  - Red: Infected users (interacted with AI content) and content generators
  - Gray: Resistant users (viewed labeled AI content)
- Chart tracking the population changes over time:
  - Green line: Users who have viewed AI content
  - Red line: Users who have interacted with AI content
  - Gray line: Users who have viewed labeled AI content
- Status display showing:
  - Current step number
  - Resistant/Susceptible Ratio
  - Infected Remaining count

## Project Structure

```
src/
├── agents.py       # Agent definitions and behaviors
├── model.py        # Core simulation model
└── app.py          # Solara visualization app

```

## Model Details

The simulation is based on a modified SIR (Susceptible-Infected-Resistant) model:

- **Agents (VirusAgent)**: Represent social media users with the following behaviors:
  - Can be exposed to AI content (transition from Susceptible to Infected)
  - Can spread content to neighbors based on content spread chance
  - Can detect AI content based on check frequency
  - Can gain resistance after exposure (labeled content awareness)

- **Network**: Erdős–Rényi random graph with configurable node count and connectivity

- **Parameters**:
  - `virus_spread_chance`: Probability of content spreading to neighbors (0.37 default)
  - `virus_check_frequency`: Frequency of content checking (0.5 default)
  - `recovery_chance`: Probability of recovery from infection (0.3 default)
  - `gain_resistance_chance`: Probability of gaining resistance (0.5 default)

## Understanding the Metrics

- **Resistant/Susceptible Ratio**: Measures the proportion of users who have viewed labeled content versus those who have only viewed unlabeled content. Higher values indicate more effective detection and labeling.

- **Infected Remaining**: Shows the current number of users interacting with and spreading AI content.

## Future Improvements

Planned enhancements:
1. Custom agent parameters for more realistic behaviors
2. Improved visualization with agent property inspection
3. Incorporation of another Mesa example to show user interactions in detail and how they result in the growth of posts
4. Adding more model parameters to make the visualization more interactive
5. Implementing multiple agent types (content generators, detectors, regular users) as separate classes with distinct behaviors and interaction patterns

## Challenges

During development, we encountered several challenges:

1. Difficulty in altering code specific to the Mesa library, especially when adapting the virus example to our content spread model
2. Implementing custom agent behaviors while maintaining compatibility with Mesa's framework
3. Balancing simulation complexity with performance considerations
4. Integrating Solara visualization components with Mesa's agent-based modeling
