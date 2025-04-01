# Battle of the AIs: Deepfake Content Spread Simulation

## Overview of the Phenomenon

Our phenomenon of interest is the spread and detection of AI-generated deepfake content on social media platforms like Instagram and Meta, with a particular focus on labeling such content and its impact. We aim to investigate if labeling AI-generated deepfake images affects its spread and whether labeling influences user behavior and interactions.

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

## Key Findings

- **Labeling Reduces Engagement Over Time**  
  Users exposed to labeled AI-generated content are more likely to disengage, reducing the overall spread.

- **Unlabeled AI Content Spreads Rapidly**  
  When AI-generated content is not labeled, engagement rates remain high, resembling viral content spread.

- **Influence of Resistant Users**  
  The presence of resistant users significantly reduces the likelihood of new users engaging with AI content.

- **Detection Accuracy & Delay**  
  - If detection models have low accuracy, content can spread more widely.
  - Labeling delay causes content to rapidly spread early in the outbreak, playing a key role in how far the content can spread before detection takes effect.

- **Social Influence**  
  Users are less likely to interact with AI content if their surrounding network does not engage with it.

- **Policy Improvements**  
  The findings suggest that social media platforms should prioritize accurate AI detection and implement clear content labeling to mitigate misinformation spread.

## Conclusion

This simulation serves as a tool to analyze the dynamic interactions between AI detection accuracy, labeling strategies, and user behavior in the spread of AI-generated content on social media. By adjusting detection thresholds, labeling latencies, and user engagement parameters, one can study how rapidly deepfake content propagates and evaluate the effectiveness of labeling policies in real-world scenarios.
